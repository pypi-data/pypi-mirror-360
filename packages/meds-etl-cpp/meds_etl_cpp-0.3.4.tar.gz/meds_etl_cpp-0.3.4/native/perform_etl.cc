#include "perform_etl.hh"

#include <bitset>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <queue>
#include <set>
#include <string>
#include <thread>

#include "absl/container/flat_hash_map.h"
#include "absl/container/flat_hash_set.h"
#include "absl/types/optional.h"
#include "arrow/array/array_binary.h"
#include "arrow/array/array_primitive.h"
#include "arrow/array/builder_binary.h"
#include "arrow/array/builder_nested.h"
#include "arrow/array/builder_primitive.h"
#include "arrow/io/file.h"
#include "arrow/memory_pool.h"
#include "arrow/record_batch.h"
#include "arrow/table.h"
#include "arrow/util/type_fwd.h"
#include "blockingconcurrentqueue.h"
#include "lightweightsemaphore.h"
#include "mmap_file.hh"
#include "parquet/arrow/reader.h"
#include "parquet/arrow/schema.h"
#include "parquet/arrow/writer.h"
#include "pdqsort.h"

namespace {

namespace fs = std::filesystem;

const size_t PARQUET_PIECE_SIZE = 10 * 1000;

std::vector<std::shared_ptr<::arrow::Field>> get_fields_for_file(
    arrow::MemoryPool* pool, const std::string& filename) {
    // Configure general Parquet reader settings
    auto reader_properties = parquet::ReaderProperties(pool);
    reader_properties.set_buffer_size(1024 * 1024);
    reader_properties.enable_buffered_stream();

    // Configure Arrow-specific Parquet reader settings
    auto arrow_reader_props = parquet::ArrowReaderProperties();
    arrow_reader_props.set_batch_size(128 * 1024);  // default 64 * 1024

    parquet::arrow::FileReaderBuilder reader_builder;
    PARQUET_THROW_NOT_OK(reader_builder.OpenFile(filename, /*memory_map=*/false,
                                                 reader_properties));
    reader_builder.memory_pool(pool);
    reader_builder.properties(arrow_reader_props);

    std::unique_ptr<parquet::arrow::FileReader> arrow_reader;
    PARQUET_ASSIGN_OR_THROW(arrow_reader, reader_builder.Build());

    const auto& manifest = arrow_reader->manifest();

    std::vector<std::shared_ptr<::arrow::Field>> fields;

    for (const auto& schema_field : manifest.schema_fields) {
        if (schema_field.children.size() != 0 || !schema_field.is_leaf()) {
            throw std::runtime_error(
                "For MEDS-Flat fields should not be nested, but we have a "
                "non-nested field " +
                schema_field.field->name());
        }

        fields.push_back(schema_field.field);
    }

    return fields;
}

const std::vector<std::string> known_fields = {"subject_id", "time"};

std::set<std::pair<std::string, std::shared_ptr<arrow::DataType>>>
get_properties_fields(const std::vector<std::string>& files) {
    arrow::MemoryPool* pool = arrow::default_memory_pool();
    std::set<std::pair<std::string, std::shared_ptr<arrow::DataType>>> result;

    for (const auto& file : files) {
        auto fields = get_fields_for_file(pool, file);
        for (const auto& field : fields) {
            if (field->name() == "value") {
                throw std::runtime_error(
                    "The C++ MEDS-Flat ETL does not currently support generic "
                    "value fields " +
                    field->ToString());
            }

            if (std::find(std::begin(known_fields), std::end(known_fields),
                          field->name()) == std::end(known_fields)) {
                result.insert(std::make_pair(field->name(), field->type()));
            }
        }
    }

    return result;
}

std::set<std::pair<std::string, std::shared_ptr<arrow::DataType>>>
get_properties_fields_multithreaded(const std::vector<std::string>& files,
                                    size_t num_threads) {
    std::vector<std::thread> threads;
    std::vector<
        std::set<std::pair<std::string, std::shared_ptr<arrow::DataType>>>>
        results(num_threads);

    size_t files_per_thread = (files.size() + num_threads - 1) / num_threads;

    for (size_t i = 0; i < num_threads; i++) {
        threads.emplace_back([&files, i, &results, files_per_thread]() {
            std::vector<std::string> fraction;
            for (size_t j = files_per_thread * i;
                 j < std::min(files.size(), files_per_thread * (i + 1)); j++) {
                fraction.push_back(files[j]);
            }
            results[i] = get_properties_fields(fraction);
        });
    }

    for (auto& thread : threads) {
        thread.join();
    }

    std::set<std::pair<std::string, std::shared_ptr<arrow::DataType>>> result;

    for (auto& res : results) {
        result.merge(std::move(res));
    }

    return result;
}

using QueueItem = absl::optional<std::vector<char>>;

constexpr int QUEUE_SIZE = 1000;
constexpr ssize_t SEMAPHORE_BLOCK_SIZE = 100;

std::map<std::string, std::pair<std::shared_ptr<arrow::DataType>, int64_t>>
get_properties(const parquet::arrow::SchemaManifest& manifest) {
    std::map<std::string, std::pair<std::shared_ptr<arrow::DataType>, int64_t>>
        result;

    std::queue<parquet::arrow::SchemaField> to_process;
    for (const auto& field : manifest.schema_fields) {
        to_process.emplace(std::move(field));
    }

    auto helper = [&](parquet::arrow::SchemaField& field) {
        if (!field.is_leaf()) {
            throw std::runtime_error(
                "meds_etl_cpp only supports leaf properties");
        }
        result[field.field->name()] =
            std::make_pair(field.field->type(), field.column_index);
    };

    while (!to_process.empty()) {
        parquet::arrow::SchemaField next = std::move(to_process.front());
        to_process.pop();
        helper(next);
    }

    return result;
}

template <typename A, typename F>
void process_string_column(const std::string& property_name,
                           const std::shared_ptr<arrow::Table>& table, F func) {
    auto chunked_values = table->GetColumnByName(property_name);

    for (const auto& array : chunked_values->chunks()) {
        auto string_array = std::dynamic_pointer_cast<A>(array);
        if (string_array == nullptr) {
            throw std::runtime_error("Could not cast property");
        }

        for (int64_t i = 0; i < string_array->length(); i++) {
            if (!string_array->IsNull(i)) {
                std::string_view item = string_array->GetView(i);
                if (!item.empty()) {
                    func(item);
                }
            }
        }
    }
}

std::vector<std::string> get_samples(
    moodycamel::BlockingConcurrentQueue<absl::optional<std::string>>&
        file_queue) {
    arrow::MemoryPool* pool = arrow::default_memory_pool();
    absl::flat_hash_map<size_t, uint8_t> string_status;

    std::vector<std::string> unique_strings;

    auto process_function = [&](std::string_view item) {
        size_t h = std::hash<decltype(item)>{}(item);
        uint8_t& value = string_status[h];

        if (value == 0) {
            value = 1;
        } else if (value == 1) {
            unique_strings.emplace_back(item);
            value = 2;
        }
    };

    absl::optional<std::string> item;
    while (true) {
        file_queue.wait_dequeue(item);

        if (!item) {
            break;
        } else {
            auto source = *item;

            // Configure general Parquet reader settings
            auto reader_properties = parquet::ReaderProperties(pool);
            reader_properties.set_buffer_size(1024 * 1024);
            reader_properties.enable_buffered_stream();

            // Configure Arrow-specific Parquet reader settings
            auto arrow_reader_props = parquet::ArrowReaderProperties();
            arrow_reader_props.set_batch_size(128 * 1024);  // default 64 * 1024

            parquet::arrow::FileReaderBuilder reader_builder;
            PARQUET_THROW_NOT_OK(reader_builder.OpenFile(
                source, /*memory_map=*/false, reader_properties));
            reader_builder.memory_pool(pool);
            reader_builder.properties(arrow_reader_props);

            std::unique_ptr<parquet::arrow::FileReader> arrow_reader;
            PARQUET_ASSIGN_OR_THROW(arrow_reader, reader_builder.Build());

            auto properties = get_properties(arrow_reader->manifest());

            std::vector<int> columns;
            std::vector<std::string> large_string_columns;
            std::vector<std::string> string_columns;

            for (const auto& entry : properties) {
                if (entry.second.first->Equals(arrow::StringType())) {
                    string_columns.push_back(entry.first);
                    columns.push_back(entry.second.second);
                } else if (entry.second.first->Equals(
                               arrow::LargeStringType())) {
                    large_string_columns.push_back(entry.first);
                    columns.push_back(entry.second.second);
                }
            }

            for (int64_t row_group = 0;
                 row_group < arrow_reader->num_row_groups(); row_group++) {
                std::shared_ptr<arrow::Table> table;
                PARQUET_THROW_NOT_OK(
                    arrow_reader->ReadRowGroup(row_group, columns, &table));

                for (const auto& s_column : string_columns) {
                    process_string_column<arrow::StringArray>(s_column, table,
                                                              process_function);
                }

                for (const auto& s_column : large_string_columns) {
                    process_string_column<arrow::LargeStringArray>(
                        s_column, table, process_function);
                }
            }
        }
    }

    return unique_strings;
}

template <typename C>
struct ChunkedArrayIterator {
    ChunkedArrayIterator(const std::shared_ptr<arrow::ChunkedArray>& a)
        : array(a) {
        chunk_index = 0;
        current_chunk = std::dynamic_pointer_cast<C>(array->chunk(chunk_index));

        if (!current_chunk) {
            throw std::runtime_error("Could not cast time array");
        }

        array_index = 0;

        update_chunk();
    }

    bool has_next() { return current_chunk != nullptr; }

    const std::shared_ptr<C>& current_array() { return current_chunk; }

    int64_t current_index() { return array_index; }

    void update_chunk() {
        while ((current_chunk != nullptr) && (array_index == current_chunk->length())) {
            chunk_index++;
            if (chunk_index < array->num_chunks()) {
                current_chunk =
                    std::dynamic_pointer_cast<C>(array->chunk(chunk_index));

                if (!current_chunk) {
                    throw std::runtime_error("Could not cast time array");
                }
            } else {
                current_chunk = nullptr;
            }

            array_index = 0;
        }
    }

    void increment() {
        array_index++;
        update_chunk();
    }

    std::shared_ptr<arrow::ChunkedArray> array;
    int chunk_index;
    std::shared_ptr<C> current_chunk;
    int64_t array_index;
};

struct ArrayEncoder {
    virtual std::optional<std::string> encode_next(
        const absl::flat_hash_map<std::string, uint32_t>& dictionary) = 0;
    virtual ~ArrayEncoder() {}
};

constexpr uint32_t DICTIONARY_MASK = ((uint32_t)(1)) << ((uint32_t)(31));

template <typename C>
struct StringRowIterator : ChunkedArrayIterator<C>, ArrayEncoder {
    StringRowIterator(const std::shared_ptr<arrow::ChunkedArray>& a)
        : ChunkedArrayIterator<C>(a) {}

    std::string_view get_next() {
        std::string_view result;
        if (this->current_array()->IsValid(this->current_index())) {
            result = this->current_array()->GetView(this->current_index());
        }
        this->increment();
        return result;
    }

    std::optional<std::string> encode_next(
        const absl::flat_hash_map<std::string, uint32_t>& dictionary) {
        auto next = get_next();
        if (next.empty()) {
            return std::nullopt;
        } else {
            auto iter = dictionary.find(next);
            if (iter != std::end(dictionary)) {
                uint32_t index = iter->second;
                return std::string(
                    std::string_view((const char*)&index, sizeof(index)));
            } else {
                uint32_t size = next.size() | DICTIONARY_MASK;

                std::string temp(
                    std::string_view((const char*)&size, sizeof(size)));
                temp.insert(std::end(temp), std::begin(next), std::end(next));

                return temp;
            }
        }
    }
};

struct PrimitiveRowIterator : ChunkedArrayIterator<arrow::PrimitiveArray>,
                              ArrayEncoder {
    PrimitiveRowIterator(const std::shared_ptr<arrow::ChunkedArray>& a)
        : ChunkedArrayIterator<arrow::PrimitiveArray>(a) {
        type_bytes = a->type()->byte_width();
    }

    int32_t type_bytes;

    std::string_view get_next() {
        std::string_view result;
        if (current_array()->IsValid(current_index())) {
            result = std::string_view(
                (const char*)current_array()->values()->data() +
                    (current_array()->offset() + current_index()) * type_bytes,
                (size_t)type_bytes);
        }
        this->increment();
        return result;
    }

    std::optional<std::string> encode_next(
        const absl::flat_hash_map<std::string, uint32_t>& dictionary) {
        auto next = get_next();
        if (next.empty()) {
            return std::nullopt;
        } else {
            return std::string(next);
        }
    }
};

template <typename C>
struct NumericRowIterator : ChunkedArrayIterator<C> {
    NumericRowIterator(const std::shared_ptr<arrow::ChunkedArray>& a)
        : ChunkedArrayIterator<C>(a) {}

    std::optional<typename C::value_type> get_next() {
        std::optional<typename C::value_type> result;
        if (this->current_array()->IsValid(this->current_index())) {
            result = this->current_array()->Value(this->current_index());
        }
        this->increment();
        return result;
    }
};

void shard_reader(
    size_t reader_index, size_t num_shards, size_t num_threads,
    moodycamel::BlockingConcurrentQueue<absl::optional<std::string>>&
        file_queue,
    std::vector<moodycamel::BlockingConcurrentQueue<QueueItem>>&
        all_write_queues,
    moodycamel::LightweightSemaphore& all_write_semaphore,
    const std::vector<std::pair<std::string, std::shared_ptr<arrow::DataType>>>&
        properties_columns,
    const absl::flat_hash_map<std::string, uint32_t>& dictionary) {
    arrow::MemoryPool* pool = arrow::default_memory_pool();

    std::vector<moodycamel::ProducerToken> ptoks;
    for (size_t i = 0; i < num_threads; i++) {
        ptoks.emplace_back(all_write_queues[i]);
    }

    ssize_t slots_to_write = all_write_semaphore.waitMany(SEMAPHORE_BLOCK_SIZE);

    absl::optional<std::string> item;
    while (true) {
        file_queue.wait_dequeue(item);

        if (!item) {
            break;
        } else {
            auto source = *item;

            // Configure general Parquet reader settings
            auto reader_properties = parquet::ReaderProperties(pool);
            reader_properties.set_buffer_size(1024 * 1024);
            reader_properties.enable_buffered_stream();

            // Configure Arrow-specific Parquet reader settings
            auto arrow_reader_props = parquet::ArrowReaderProperties();
            arrow_reader_props.set_batch_size(128 * 1024);  // default 64 * 1024

            parquet::arrow::FileReaderBuilder reader_builder;
            PARQUET_THROW_NOT_OK(reader_builder.OpenFile(
                source, /*memory_map=*/false, reader_properties));
            reader_builder.memory_pool(pool);
            reader_builder.properties(arrow_reader_props);

            std::unique_ptr<parquet::arrow::FileReader> arrow_reader;
            PARQUET_ASSIGN_OR_THROW(arrow_reader, reader_builder.Build());

            std::vector<int> properties_indices(properties_columns.size(), -1);

            for (int64_t row_group = 0;
                 row_group < arrow_reader->num_row_groups(); row_group++) {
                std::shared_ptr<arrow::Table> table;
                PARQUET_THROW_NOT_OK(
                    arrow_reader->ReadRowGroup(row_group, &table));

                NumericRowIterator<arrow::Int64Array> subject_id_column(
                    table->GetColumnByName("subject_id"));
                NumericRowIterator<arrow::TimestampArray> time_column(
                    table->GetColumnByName("time"));

                auto time_type =
                    std::dynamic_pointer_cast<arrow::TimestampType>(
                        table->GetColumnByName("time")->type());

                if (time_type->unit() != arrow::TimeUnit::MICRO) {
                    throw std::runtime_error("Wrong units for timestamp");
                }

                if (!time_type->timezone().empty()) {
                    throw std::runtime_error("Need an empty timezone");
                }

                std::vector<std::pair<size_t, std::unique_ptr<ArrayEncoder>>>
                    encoders;

                for (size_t i = 0; i < properties_columns.size(); i++) {
                    const auto& property = properties_columns[i];

                    auto chunks = table->GetColumnByName(property.first);

                    if (!chunks) {
                        continue;
                    }

                    if (property.second->Equals(arrow::StringType())) {
                        encoders.emplace_back(
                            i,
                            std::make_unique<
                                StringRowIterator<arrow::StringArray>>(chunks));
                    } else if (property.second->Equals(
                                   arrow::LargeStringType())) {
                        encoders.emplace_back(
                            i, std::make_unique<
                                   StringRowIterator<arrow::LargeStringArray>>(
                                   chunks));
                    } else {
                        encoders.emplace_back(
                            i, std::make_unique<PrimitiveRowIterator>(chunks));
                    }
                }

                while (subject_id_column.has_next()) {
                    auto possible_subject_id = subject_id_column.get_next();
                    if (!possible_subject_id) {
                        throw std::runtime_error("Missing a subject id value");
                    }

                    int64_t subject_id = *possible_subject_id;
                    std::optional<int64_t> possible_time =
                        time_column.get_next();

                    int64_t time = std::numeric_limits<int64_t>::min();
                    if (possible_time) {
                        time = *possible_time;
                    }

                    std::bitset<64> is_valid;
                    std::vector<char> result(sizeof(uint64_t) * 3);

                    {
                        int64_t* id_map = (int64_t*)(result.data());
                        id_map[0] = subject_id;
                        id_map[1] = time;
                    }

                    for (auto& encoder : encoders) {
                        auto entry = encoder.second->encode_next(dictionary);
                        if (entry) {
                            is_valid.set(encoder.first);
                            result.insert(std::end(result), std::begin(*entry),
                                          std::end(*entry));
                        }
                    }

                    uint64_t* null_map =
                        (uint64_t*)(result.data() + sizeof(int64_t) * 2);

                    *null_map = is_valid.to_ulong();

                    size_t index =
                        std::hash<int64_t>()(subject_id) % num_shards;
                    size_t thread_index = index % num_threads;

                    all_write_queues[thread_index].enqueue(ptoks[thread_index],
                                                           std::move(result));

                    slots_to_write--;
                    if (slots_to_write == 0) {
                        slots_to_write =
                            all_write_semaphore.waitMany(SEMAPHORE_BLOCK_SIZE);
                    }
                }
            }
        }
    }

    for (size_t j = 0; j < num_threads; j++) {
        all_write_queues[j].enqueue(ptoks[j], absl::nullopt);
    }

    if (slots_to_write > 0) {
        all_write_semaphore.signal(slots_to_write);
    }
}

void shard_writer(size_t writer_index, size_t num_shards, size_t num_threads,
                  moodycamel::BlockingConcurrentQueue<QueueItem>& write_queue,
                  moodycamel::LightweightSemaphore& write_semaphore,
                  const std::filesystem::path& target_dir) {
    std::filesystem::create_directory(target_dir);

    std::vector<std::ofstream> subshards;

    for (size_t i = writer_index; i < num_shards; i += num_threads) {
        auto target_file = target_dir / std::to_string(i);
        subshards.emplace_back(target_file, std::ios_base::binary);
    }

    QueueItem item;
    size_t readers_remaining = num_threads;

    moodycamel::ConsumerToken ctok(write_queue);

    size_t num_read = 0;

    while (true) {
        write_queue.wait_dequeue(ctok, item);

        if (!item) {
            readers_remaining--;
            if (readers_remaining == 0) {
                break;
            } else {
                continue;
            }
        }

        num_read++;
        if (num_read == SEMAPHORE_BLOCK_SIZE) {
            write_semaphore.signal(num_read);
            num_read = 0;
        }

        std::vector<char>& r = *item;
        int64_t* subject_id_ptr = (int64_t*)r.data();
        int64_t subject_id = *subject_id_ptr;

        size_t shard = std::hash<int64_t>()(subject_id) % num_shards;
        size_t index = shard / num_threads;
        int64_t size = r.size();
        subshards[index].write((const char*)&size, sizeof(size));
        subshards[index].write(r.data(), r.size());
    }

    write_semaphore.signal(num_read);
}

std::pair<absl::flat_hash_map<std::string, uint32_t>, std::vector<std::string>>
compute_string_dictionary(const std::filesystem::path& source_directory,
                          size_t num_threads) {
    std::vector<std::string> paths;

    for (const auto& entry : fs::directory_iterator(source_directory)) {
        paths.push_back(entry.path());
    }

    moodycamel::BlockingConcurrentQueue<absl::optional<std::string>> file_queue;

    for (const auto& path : paths) {
        file_queue.enqueue(path);
    }

    for (size_t i = 0; i < num_threads; i++) {
        file_queue.enqueue({});
    }

    std::vector<std::vector<std::string>> strings_per_thread(num_threads);
    std::vector<std::thread> threads;

    for (size_t i = 0; i < num_threads; i++) {
        threads.emplace_back([i, &file_queue, &strings_per_thread]() {
            strings_per_thread[i] = get_samples(file_queue);
        });
    }

    for (auto& thread : threads) {
        thread.join();
    }

    std::vector<std::string> dictionary_entries;

    absl::flat_hash_map<std::string, uint32_t> unique_entries;
    uint32_t next_index = 0;

    for (auto& entry : strings_per_thread) {
        for (auto& s : entry) {
            auto e = unique_entries.try_emplace(s, next_index);
            if (e.second) {
                next_index++;
                dictionary_entries.emplace_back(std::move(s));
            }
        }
    }

    return {unique_entries, dictionary_entries};
}

std::pair<std::vector<std::pair<std::string, std::shared_ptr<arrow::DataType>>>,
          std::vector<std::string>>
sort_and_shard(const std::filesystem::path& source_directory,
               const std::filesystem::path& target_directory, size_t num_shards,
               size_t num_threads) {
    auto dictionary_and_entries =
        compute_string_dictionary(source_directory, num_threads);
    const absl::flat_hash_map<std::string, uint32_t>& string_dictionary =
        dictionary_and_entries.first;

    std::filesystem::create_directory(target_directory);

    std::vector<std::string> paths;

    for (const auto& entry : fs::directory_iterator(source_directory)) {
        paths.push_back(entry.path());
    }

    auto set_properties_fields =
        get_properties_fields_multithreaded(paths, num_threads);

    std::vector<std::pair<std::string, std::shared_ptr<arrow::DataType>>>
        properties_columns(std::begin(set_properties_fields),
                           std::end(set_properties_fields));
    std::sort(std::begin(properties_columns), std::end(properties_columns));

    properties_columns.erase(std::unique(std::begin(properties_columns),
                                         std::end(properties_columns),
                                         [](const auto& a, const auto& b) {
                                             return (a.first == b.first) &&
                                                    a.second->Equals(b.second);
                                         }),
                             std::end(properties_columns));

    for (ssize_t i = 0; i < static_cast<ssize_t>(properties_columns.size()) - 1;
         i++) {
        if (properties_columns[i].first == properties_columns[i + 1].first) {
            throw std::runtime_error(
                "Got conflicting types for column " +
                properties_columns[i].first +
                ", types: " + properties_columns[i].second->ToString() +
                " vs " + properties_columns[i + 1].second->ToString());
        }
    }

    auto add_and_force = [&](const std::string& name,
                             std::shared_ptr<arrow::DataType> type,
                             bool add_back = true) {
        auto code_iter = std::find_if(
            std::begin(properties_columns), std::end(properties_columns),
            [&name](const auto& entry) { return entry.first == name; });

        if (code_iter != std::end(properties_columns)) {
            if (type->Equals(arrow::StringType()) &&
                code_iter->second->Equals(arrow::LargeStringType())) {
                // Hack to work around this
                type = std::make_shared<arrow::LargeStringType>();
            }

            if (!code_iter->second->Equals(type)) {
                throw std::runtime_error("For column " + name +
                                         " got unexpected type " +
                                         code_iter->second->ToString());
            }
            properties_columns.erase(code_iter);
        }

        if (add_back) {
            properties_columns.insert(std::begin(properties_columns),
                                      std::make_pair(name, type));
        }
    };

    add_and_force("numeric_value", std::make_shared<arrow::FloatType>());
    add_and_force("code", std::make_shared<arrow::StringType>());
    add_and_force(
        "time", std::make_shared<arrow::TimestampType>(arrow::TimeUnit::MICRO),
        false);
    add_and_force("subject_id", std::make_shared<arrow::Int64Type>(), false);

    if (properties_columns.size() > std::numeric_limits<uint64_t>::digits) {
        throw std::runtime_error(
            "C++ MEDS-ETL currently only supports at most " +
            std::to_string(std::numeric_limits<uint64_t>::digits) +
            " properties columns");
    }

    moodycamel::BlockingConcurrentQueue<absl::optional<std::string>> file_queue;

    for (const auto& path : paths) {
        file_queue.enqueue(path);
    }

    for (size_t i = 0; i < num_threads; i++) {
        file_queue.enqueue({});
    }

    std::vector<moodycamel::BlockingConcurrentQueue<QueueItem>> write_queues(
        num_threads);

    std::vector<std::thread> threads;

    moodycamel::LightweightSemaphore write_semaphore(QUEUE_SIZE * num_threads);

    for (size_t i = 0; i < num_threads; i++) {
        threads.emplace_back([i, &file_queue, &write_queues, &write_semaphore,
                              num_shards, num_threads, &properties_columns,
                              &string_dictionary]() {
            shard_reader(i, num_shards, num_threads, file_queue, write_queues,
                         write_semaphore, properties_columns,
                         string_dictionary);
        });

        threads.emplace_back([i, &write_queues, &write_semaphore, num_shards,
                              num_threads, target_directory]() {
            shard_writer(i, num_shards, num_threads, write_queues[i],
                         write_semaphore, target_directory);
        });
    }

    for (auto& thread : threads) {
        thread.join();
    }

    return {properties_columns, dictionary_and_entries.second};
}

void join_and_write_single(
    const std::filesystem::path& source_path,
    const std::filesystem::path& target_path,
    const std::vector<std::pair<std::string, std::shared_ptr<arrow::DataType>>>&
        properties_columns,
    const std::vector<std::string>& dictionary_entries) {
    MmapFile data(source_path);
    if (data.bytes().size() == 0) {
        return;
    }

    arrow::MemoryPool* pool = arrow::default_memory_pool();

    auto timestamp_type =
        std::make_shared<arrow::TimestampType>(arrow::TimeUnit::MICRO);

    arrow::FieldVector properties_fields = {
        arrow::field("subject_id", std::make_shared<arrow::Int64Type>()),
        arrow::field("time", timestamp_type),
    };

    auto subject_id_builder = std::make_shared<arrow::Int64Builder>(pool);
    auto time_builder =
        std::make_shared<arrow::TimestampBuilder>(timestamp_type, pool);

    std::vector<std::shared_ptr<arrow::ArrayBuilder>> builders = {
        subject_id_builder, time_builder};

    std::vector<std::function<const char*(const char*)>> writers;

    for (size_t i = 0; i < properties_columns.size(); i++) {
        const auto& properties_column = properties_columns[i];
        if (properties_column.second->Equals(arrow::StringType()) ||
            properties_column.first == "code") {
            auto string_builder = std::make_shared<arrow::StringBuilder>(pool);

            auto writer = [string_builder, &dictionary_entries](
                              const char* data) -> const char* {
                if (data == nullptr) {
                    PARQUET_THROW_NOT_OK(string_builder->AppendNull());
                    return nullptr;
                } else {
                    uint32_t size = *(uint32_t*)data;
                    if ((size & DICTIONARY_MASK) == 0) {
                        PARQUET_THROW_NOT_OK(
                            string_builder->Append(dictionary_entries[size]));
                        return data + sizeof(uint32_t);
                    } else {
                        PARQUET_THROW_NOT_OK(string_builder->Append(
                            std::string_view(data + sizeof(uint32_t),
                                             size & ~DICTIONARY_MASK)));
                        return data + sizeof(uint32_t) +
                               (size & ~DICTIONARY_MASK);
                    }
                }
            };

            writers.emplace_back(std::move(writer));
            builders.emplace_back(std::move(string_builder));
        } else if (properties_column.second->Equals(arrow::LargeStringType())) {
            auto string_builder =
                std::make_shared<arrow::LargeStringBuilder>(pool);

            auto writer = [string_builder, &dictionary_entries](
                              const char* data) -> const char* {
                if (data == nullptr) {
                    PARQUET_THROW_NOT_OK(string_builder->AppendNull());
                    return nullptr;
                } else {
                    uint32_t size = *(uint32_t*)data;
                    if ((size & DICTIONARY_MASK) == 0) {
                        PARQUET_THROW_NOT_OK(
                            string_builder->Append(dictionary_entries[size]));
                        return data + sizeof(uint32_t);
                    } else {
                        PARQUET_THROW_NOT_OK(string_builder->Append(
                            std::string_view(data + sizeof(uint32_t),
                                             size & ~DICTIONARY_MASK)));
                        return data + sizeof(uint32_t) +
                               (size & ~DICTIONARY_MASK);
                    }
                }
            };

            writers.emplace_back(std::move(writer));
            builders.emplace_back(std::move(string_builder));
        } else {
            auto primitive_builder =
                std::make_shared<arrow::FixedSizeBinaryBuilder>(
                    std::make_shared<arrow::FixedSizeBinaryType>(
                        properties_column.second->byte_width()));
            int num_bytes = properties_column.second->byte_width();
            auto writer = [primitive_builder,
                           num_bytes](const char* data) -> const char* {
                if (data == nullptr) {
                    PARQUET_THROW_NOT_OK(primitive_builder->AppendNull());
                    return nullptr;
                } else {
                    PARQUET_THROW_NOT_OK(primitive_builder->Append(data));
                    return data + num_bytes;
                }
            };

            writers.emplace_back(std::move(writer));
            builders.emplace_back(std::move(primitive_builder));
        }

        if (properties_column.first == "code") {
            properties_fields.push_back(
                arrow::field(properties_column.first,
                             std::make_shared<arrow::StringType>()));

        } else {
            properties_fields.push_back(arrow::field(properties_column.first,
                                                     properties_column.second));
        }
    }

    auto schema = std::make_shared<arrow::Schema>(properties_fields);

    using parquet::ArrowWriterProperties;
    using parquet::WriterProperties;

    size_t amount_written = 0;

    // Choose compression
    std::shared_ptr<WriterProperties> props =
        WriterProperties::Builder()
            .compression(arrow::Compression::ZSTD)
            ->build();

    // Opt to store Arrow schema for easier reads back into Arrow
    std::shared_ptr<ArrowWriterProperties> arrow_props =
        ArrowWriterProperties::Builder().store_schema()->build();

    // Create a writer
    std::shared_ptr<arrow::io::FileOutputStream> outfile;
    PARQUET_ASSIGN_OR_THROW(
        outfile, arrow::io::FileOutputStream::Open(target_path.string()));
    std::unique_ptr<parquet::arrow::FileWriter> writer;
    PARQUET_ASSIGN_OR_THROW(
        writer, parquet::arrow::FileWriter::Open(*schema, pool, outfile, props,
                                                 arrow_props));

    auto flush_arrays = [&]() {
        std::vector<std::shared_ptr<arrow::Array>> columns(builders.size());
        for (size_t i = 0; i < builders.size(); i++) {
            PARQUET_THROW_NOT_OK(builders[i]->Finish(columns.data() + i));
            PARQUET_ASSIGN_OR_THROW(
                columns[i], columns[i]->View(properties_fields[i]->type()));
        }

        std::shared_ptr<arrow::Table> table =
            arrow::Table::Make(schema, columns);

        PARQUET_THROW_NOT_OK(writer->WriteTable(*table));

        amount_written = 0;
    };

    std::vector<std::tuple<int64_t, int64_t, std::string_view>> events;

    const char* pointer = data.bytes().begin();

    while (pointer != data.bytes().end()) {
        int64_t* header = (int64_t*)pointer;
        int64_t size = header[0];
        int64_t subject_id = header[1];
        int64_t time = header[2];

        pointer += sizeof(int64_t);

        size_t subject_and_time_size = sizeof(int64_t) * 2;

        events.push_back(std::make_tuple(
            subject_id, time,
            std::string_view(pointer + subject_and_time_size, size - subject_and_time_size)));

        pointer += size;
    }

    pdqsort_branchless(std::begin(events), std::end(events));

    for (const auto& event : events) {
        int64_t subject_id = std::get<0>(event);
        int64_t time = std::get<1>(event);
        std::string_view subject_record = std::get<2>(event);

        amount_written++;

        if (amount_written > PARQUET_PIECE_SIZE) {
            flush_arrays();
        }

        PARQUET_THROW_NOT_OK(subject_id_builder->Append(subject_id));
        if (time == std::numeric_limits<int64_t>::min()) {
            PARQUET_THROW_NOT_OK(time_builder->AppendNull());
        } else {
            PARQUET_THROW_NOT_OK(time_builder->Append(time));
        }

        const char* data = subject_record.data();

        uint64_t* null_byte_pointer = (uint64_t*)data;
        std::bitset<64> is_valid(*null_byte_pointer);

        data += sizeof(uint64_t);

        for (size_t i = 0; i < writers.size(); i++) {
            if (is_valid.test(i)) {
                data = writers[i](data);
            } else {
                writers[i](nullptr);
            }
        }
    }

    flush_arrays();

    // Write file footer and close
    PARQUET_THROW_NOT_OK(writer->Close());
}

void join_and_write(
    const std::filesystem::path& source_directory,
    const std::filesystem::path& target_directory,
    const std::vector<std::pair<std::string, std::shared_ptr<arrow::DataType>>>&
        properties_columns,
    const std::vector<std::string>& dictionary_entries, size_t num_threads) {
    std::filesystem::create_directory(target_directory);

    moodycamel::BlockingConcurrentQueue<absl::optional<std::string>> file_queue;

    for (const auto& entry : fs::directory_iterator(source_directory)) {
        file_queue.enqueue(fs::relative(entry.path(), source_directory));
    }

    std::vector<std::thread> threads;

    for (size_t i = 0; i < num_threads; i++) {
        file_queue.enqueue({});
        threads.emplace_back([&file_queue, &source_directory, &target_directory,
                              &properties_columns, &dictionary_entries]() {
            absl::optional<std::string> item;
            while (true) {
                file_queue.wait_dequeue(item);

                if (!item) {
                    break;
                }

                join_and_write_single(source_directory / *item,
                                      target_directory / (*item + ".parquet"),
                                      properties_columns, dictionary_entries);
            }
        });
    }

    for (auto& thread : threads) {
        thread.join();
    }
}

}  // namespace

void perform_etl(const std::string& source_directory,
                 const std::string& target_directory, size_t num_shards,
                 size_t num_threads) {
    std::filesystem::path source_path(source_directory);
    std::filesystem::path target_path(target_directory);

    std::filesystem::create_directory(target_path);

    if (fs::exists(source_path / "metadata")) {
        fs::copy(source_path / "metadata", target_path / "metadata");
    }

    std::filesystem::path shard_path = target_path / "shards";
    std::filesystem::path data_path = target_path / "data";

    auto properties_columns_and_dictionary = sort_and_shard(
        source_path / "unsorted_data", shard_path, num_shards, num_threads);

    join_and_write(shard_path, data_path,
                   properties_columns_and_dictionary.first,
                   properties_columns_and_dictionary.second, num_threads);

    fs::remove_all(shard_path);
}

#pragma once

#include <string>

void perform_etl(const std::string& source_directory,
                 const std::string& target_directory, size_t num_shards,
                 size_t num_threads);
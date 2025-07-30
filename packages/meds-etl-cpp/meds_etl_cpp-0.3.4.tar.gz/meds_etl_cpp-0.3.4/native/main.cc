#include "perform_etl.hh"

int main() {
    std::string path_to_folder =
        "/home/ethanid/extracts/mimic_extract3/temp/";
    std::string output = "/home/ethanid/extracts/test_me_extract";

    perform_etl(path_to_folder, output, 1000, 12);
}

#include <pybind11/pybind11.h>

#include "perform_etl.hh"

PYBIND11_MODULE(meds_etl_cpp, m) { m.def("perform_etl", perform_etl); }
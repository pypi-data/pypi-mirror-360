#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "mes_utils.hpp"
#include "mes_utils_precomputed.hpp"
#include "mes_add1.hpp"

namespace py = pybind11;

PYBIND11_MODULE(muoblpbindings, m) {
    m.def("equal_shares_utils", &equal_shares_utils);
    m.def("equal_shares_utils_precomputed", &equal_shares_utils_precomputed);
    m.def("equal_shares_add1", &equal_shares_add1);
}

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>
#include "rate4site.h"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

py::array_t<double> run_rate4site(char msa[],  char *inTreeFile, char *outTreeFile) {
    rate4site r4s(msa, inTreeFile, outTreeFile);
    std::vector<double> vec = r4s.compute();
    return py::array_t<double>(vec.size(), vec.data());
}


PYBIND11_MODULE(pyrate4site, m) {
    m.doc() = R"pbdoc(
        Rate4Site Plugin
        -----------------------

        .. currentmodule:: pyrate4site

        .. autosummary::
           :toctree: _generate

    )pbdoc";

    m.def("rate4site", &run_rate4site, R"pbdoc(
        Compute Rate4site

    )pbdoc", py::arg("msa"),  py::arg("inTreeFile") = nullptr,  py::arg("outTreeFile") = nullptr);

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif

}
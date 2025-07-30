// python/msamdd/wrapper_cnv.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

// -----------------------------------------------------------------------------
// declare the “C” entry‐point from your convex‐gap binary
extern "C" int main_convex(int argc, char** argv);

namespace py = pybind11;

PYBIND11_MODULE(_optmsa_cnv, m) {
    m.doc() = "MSAMDD convex-gap alignment";

    m.def("run_convex",
        [](const std::vector<std::string>& flags) {
            std::vector<const char*> argv;
            argv.reserve(flags.size() + 1);
            argv.push_back("optmsa_cnv");
            for (auto& s : flags)
                argv.push_back(s.c_str());
            return main_convex((int)argv.size(),
                               const_cast<char**>(argv.data()));
        },
        py::arg("flags") = std::vector<std::string>{}
    );
}

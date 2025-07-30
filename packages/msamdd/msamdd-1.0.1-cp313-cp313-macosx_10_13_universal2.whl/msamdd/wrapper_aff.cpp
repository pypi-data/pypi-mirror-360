// python/msamdd/wrapper_aff.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

// -----------------------------------------------------------------------------
// declare the “C” entry‐point from your affine‐gap binary
extern "C" int main_affine(int argc, char** argv);

namespace py = pybind11;

PYBIND11_MODULE(_optmsa_aff, m) {
    m.doc() = "MSAMDD affine-gap alignment";

    m.def("run_affine",
        [](const std::vector<std::string>& flags) {
            std::vector<const char*> argv;
            argv.reserve(flags.size() + 1);
            argv.push_back("optmsa_aff");
            for (auto& s : flags)
                argv.push_back(s.c_str());
            return main_affine((int)argv.size(),
                               const_cast<char**>(argv.data()));
        },
        py::arg("flags") = std::vector<std::string>{}
    );
}

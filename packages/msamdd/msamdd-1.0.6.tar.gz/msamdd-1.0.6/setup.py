# setup.py  – MSAMDD
# Build two Pybind11 extensions that link against IBM CPLEX 22.1.x (static or dynamic).

from pathlib import Path
from setuptools import setup, Extension, find_packages
import glob, os, sys, pybind11

# ─────────────────────────────────────────────
# 1)  Locate a CPLEX install
# ─────────────────────────────────────────────
def find_cplex_root() -> Path | None:
    # honour env-vars first
    for var in ("CPLEX_STUDIO_DIR221", "CPLEX_ROOT"):
        p = os.getenv(var)
        if p:
            return Path(p)

    # otherwise probe standard macOS locations (both Community & commercial)
    for patt in (
        "/Applications/CPLEX_Studio*221*/",            # commercial 22.1.2, 22.1.1 …
        "/Applications/CPLEX_Studio_Community221*/",   # community
    ):
        for p in Path("/Applications").glob(patt):
            return p
    return None


CPLEX_DIR = find_cplex_root()
if CPLEX_DIR is None:
    raise RuntimeError(
        "IBM CPLEX 22.1.x not found.\n"
        "Install it first and/or set the env-var CPLEX_STUDIO_DIR221."
    )

# ─────────────────────────────────────────────
# 2)  Platform-specific include / lib dirs
# ─────────────────────────────────────────────
arch_dir = "arm64_osx" if sys.platform == "darwin" and "arm64" in os.uname().machine else "x86-64_osx"

CPLEX_INC    = CPLEX_DIR / "cplex"   / "include"
CONCERT_INC  = CPLEX_DIR / "concert" / "include"
CPLEX_LIB    = CPLEX_DIR / "cplex"   / "lib" / arch_dir / "static_pic"
CONCERT_LIB  = CPLEX_DIR / "concert" / "lib" / arch_dir / "static_pic"
OPL_INC     = CPLEX_DIR / "opl"     / "include" #added new


include_dirs = [
    pybind11.get_include(),
    *map(str, (CPLEX_INC, CONCERT_INC, OPL_INC)),
    "src", "src/src_aff", "src/src_cnv",
]
library_dirs = [str(CPLEX_LIB), str(CONCERT_LIB)]
libraries    = ["cplex", "ilocplex", "concert"]
extra_cxx    = ["-std=c++17"]

# ─────────────────────────────────────────────
# 3)  Helper for the two extensions
# ─────────────────────────────────────────────
def make_ext(py_name: str, src_glob: str, wrapper_cpp: str) -> Extension:
    sources = glob.glob(src_glob) + [wrapper_cpp]
    return Extension(
        f"msamdd.{py_name}",
        sources=sources,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        extra_compile_args=extra_cxx,
        language="c++",
    )

ext_modules = [
    make_ext("_optmsa_aff", "src/src_aff/*.cpp", "python/msamdd/wrapper_aff.cpp"),
    make_ext("_optmsa_cnv", "src/src_cnv/*.cpp", "python/msamdd/wrapper_cnv.cpp"),
]

# ─────────────────────────────────────────────
# 4)  Setup-meta
# ─────────────────────────────────────────────
setup(
    name="msamdd",
    version="1.0.6",
    description="Exact multiple sequence alignment via Synchronized Decision Diagrams",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Yeswanth Vootla",
    author_email="vootlayeswanth20@gmail.com",
    license="GPL-2.0-or-later",
    python_requires=">=3.8, <3.13",          # cplex wheels exist only up to 3.12
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    include_package_data=True,               # relies on MANIFEST.in (keep your graft + headers rules)
    ext_modules=ext_modules,
    install_requires=[
        "pybind11>=2.6",
        "cplex>=22.1.1",
    ],
    entry_points={
        "console_scripts": [
            "msa_aff = msamdd.cli_aff:main",
            "msa_cnv = msamdd.cli_cnv:main",
        ],
    },
    zip_safe=False,
)

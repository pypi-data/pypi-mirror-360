# setup.py  –  MSAMDD library
# ------------------------------------------------------------
# Build two Pybind11 extensions that link against IBM CPLEX
# Community Edition (static .a files) on macOS / Apple Silicon.
# ------------------------------------------------------------
from pathlib import Path
from setuptools import setup, Extension, find_packages
import os, sys, glob, pybind11

# ─────────────────────────────────────────────────────────────
# 1) Locate IBM ILOG CPLEX Optimization Studio
# ─────────────────────────────────────────────────────────────
CPLEX_DIR = (
    os.getenv("CPLEX_STUDIO_DIR221")      # IBM’s default env-var
    or os.getenv("CPLEX_ROOT")            # legacy env-var
    or next((Path("/Applications").glob("CPLEX_Studio_*")), None)
)

if not CPLEX_DIR:
    raise RuntimeError(
        "CPLEX install not found.  Set CPLEX_STUDIO_DIR221 (or CPLEX_ROOT) "
        "to the root of IBM ILOG CPLEX Optimization Studio."
    )

CPLEX_DIR = Path(CPLEX_DIR)

# ─────────────────────────────────────────────────────────────
# 2) Platform-specific sub-folder and header / lib paths
#    (Community Edition ships only static .a libraries)
# ─────────────────────────────────────────────────────────────
if sys.platform == "darwin":
    arch_dir = "arm64_osx" if "arm64" in os.uname().machine else "x86-64_osx"
elif sys.platform.startswith("linux"):
    arch_dir = "x86-64_linux"
elif sys.platform.startswith("win"):
    arch_dir = "x64_windows_vs2019"
else:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

CPLEX_INC   = CPLEX_DIR / "cplex"   / "include"
CONCERT_INC = CPLEX_DIR / "concert" / "include"

#  → point library dirs at *static_pic*
CPLEX_LIB   = CPLEX_DIR / "cplex"   / "lib" / arch_dir / "static_pic"
CONCERT_LIB = CPLEX_DIR / "concert" / "lib" / arch_dir / "static_pic"

include_dirs = [
    pybind11.get_include(),
    str(CPLEX_INC),
    str(CONCERT_INC),
    "src",
    "src/src_aff",           # ← added: contains benders.hpp, etc.
    "src/src_cnv",           # ← added
]

library_dirs = [str(CPLEX_LIB), str(CONCERT_LIB)]

# static libs = plain short names (no version tag)
libraries    = ["cplex", "ilocplex", "concert"]
extra_cxx    = ["-std=c++17"]

# ─────────────────────────────────────────────────────────────
# 3) Helper to create each Extension
# ─────────────────────────────────────────────────────────────
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

extensions = [
    make_ext("_optmsa_aff", "src/src_aff/*.cpp", "python/msamdd/wrapper_aff.cpp"),
    make_ext("_optmsa_cnv", "src/src_cnv/*.cpp", "python/msamdd/wrapper_cnv.cpp"),
]

# ─────────────────────────────────────────────────────────────
# 4) Package metadata
# ─────────────────────────────────────────────────────────────
setup(
    name="msamdd",
    version="1.0.1",
    description="Exact multiple sequence alignment via Synchronized Decision Diagrams",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Yeswanth Vootla",
    author_email="vootlayeswanth20@gmail.com",
    license="GPL-2.0-or-later",
    python_requires=">=3.8",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    include_package_data=True, 
    ext_modules=extensions,
    install_requires=[
        "pybind11>=2.6",
        "cplex>=22.1.1",      # pulls IBM’s pure-Python API from PyPI
    ],
    zip_safe=False,
)

# python/msamdd/__init__.py

from ._optmsa_cnv      import run_convex
from ._optmsa_aff      import run_affine

__all__ = (
    "run_convex",
    "run_affine",
)

# Optionally give them friendlier aliases:
def convex(*flags: str) -> int:
    """Run the convex solver with a list of command-line flags."""
    return run_convex.run_from_argv(list(flags))

def affine(*flags: str) -> int:
    """Run the affine solver with a list of command-line flags."""
    return run_affine.run_from_argv(list(flags))

__all__ += ("convex", "affine")

# Version string
__version__ = "1.1.0"

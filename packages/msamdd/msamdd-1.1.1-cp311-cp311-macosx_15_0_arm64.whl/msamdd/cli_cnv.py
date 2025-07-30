from msamdd._optmsa_cnv import run_convex
import sys

def main() -> None:
    args = sys.argv[1:]
    # stub‐level help: print the extension’s docstring
    if "-h" in args or "--help" in args:
        print(run_convex.__doc__)
        sys.exit(0)
    sys.exit(run_convex(args))

from msamdd._optmsa_aff import run_affine
import sys

def main() -> None:
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(run_affine.__doc__)
        sys.exit(0)
    sys.exit(run_affine(args))

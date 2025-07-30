# python/msamdd/cli_aff.py
from msamdd import msa_aff  # ← whatever function you want to call
import sys

def main() -> None:
    sys.exit(msa_aff.run_from_argv(sys.argv[1:]))   # or however you invoke it

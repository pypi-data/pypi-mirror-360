# python/msamdd/cli_cnv.py
from msamdd import msa_cnv
import sys

def main() -> None:
    sys.exit(msa_cnv.run_from_argv(sys.argv[1:]))

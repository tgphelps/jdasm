
import sys
from typing import NoReturn

from Globals import g


def fatal(*args) -> NoReturn:
    "Print and log the error message, and terminate."
    msg = 'FATAL: ' + ' '.join(str(x) for x in args)
    print(msg, file=sys.stderr)
    if g.debug:
        g.log.log(msg)
    exit(2)


def gen_output_file_name(infile: str) -> str:
    """
    Generate the output source filename from the input filename.

    If the input name ends with '.class', change that ending to '.j'.
    Otherwise, append '.j' to the filename.
    """
    if infile.endswith('.class'):
        infile = infile[0:-6]
    return infile + '.j'

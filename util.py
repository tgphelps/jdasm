
import sys
from typing import NoReturn

from Globals import g


def fatal(*args) -> NoReturn:
    msg = 'FATAL: ' + ' '.join(str(x) for x in args)
    print(msg, file=sys.stderr)
    if g.debug:
        g.log.log(msg)
    exit(2)

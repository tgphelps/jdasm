
# YES, Globals.py must be capitalized, because
# 'import globals' does not work.

from log import Log


class Globals:
    args: dict[str, str]
    debug: bool
    log: Log


g = Globals()

import sys
from datetime import datetime

debug_flag = False


def info(s):
    stderr_print(f"{datetime.now().strftime('%H:%M:%S')} [INFO] {s}")


def error(s):
    stderr_print(f"{datetime.now().strftime('%H:%M:%S')} [ERROR] {s}")


def fatal(s):
    error(s)
    sys.exit(1)


def debug(s):
    if debug_flag:
        stderr_print(f"{datetime.now().strftime('%H:%M:%S')} [DEBUG] {s}")


def stderr_print(s):
    print(s, file=sys.stderr)

import sys
from datetime import datetime


def info(s):
    stderr_print(f"{datetime.now().strftime('%H:%M:%S')} [INFO] {s}")


def stderr_print(s):
    print(s, file=sys.stderr)
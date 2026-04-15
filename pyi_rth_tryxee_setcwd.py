import os
import sys


def _try_set_cwd_to_meipass():
    base = getattr(sys, "_MEIPASS", None)
    if base and os.path.isdir(base):
        try:
            os.chdir(base)
        except Exception:
            pass


_try_set_cwd_to_meipass()

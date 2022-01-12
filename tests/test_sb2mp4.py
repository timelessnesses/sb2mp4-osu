import os

import pytest


def test():
    if os.system(r"sb2mp4.py 'tests\test_bm' ") != 0:
        raise Exception("sb2mp4.py failed")

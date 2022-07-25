#!/usr/bin/env python3
import os

from check_invar import diff_src

if __name__ == "__main__":
    ret = diff_src(os.environ["creduce_target"])
    if not any(ret):
        exit(1)

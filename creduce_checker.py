#!/usr/bin/env python3
import os

from check_invar import diff_src

if __name__ == "__main__":
    reduce_expr = tuple(int(i) for i in os.environ["reduce_expr"].split(" "))
    ret = diff_src(os.environ["creduce_target"])
    if tuple(len(i) for i in ret) != reduce_expr:
        exit(1)

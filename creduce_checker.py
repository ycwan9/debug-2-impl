#!/usr/bin/env python3
import os

from check_invar import diff_src


def check_cnt(target):
    reduce_expr = tuple(int(i) for i in os.environ["reduce_expr"].split(" "))
    ret = diff_src(target)
    if tuple(len(i) for i in ret) != reduce_expr:
        exit(1)


def check_1st(target):
    from opt_bisect import check_violation
    pass_num = int(os.environ("reduce_expr"))
    if not check_violation(target, pass_num):
        exit(1)


def check_plain(target):
    ret = diff_src(target)
    if not any(ret):
        exit(1)


if __name__ == "__main__":
    check_method = os.getenv("REDUCE_METHOD")
    target = os.environ["creduce_target"]
    {
        "1st": check_1st,
        "cnt": check_cnt
    }.get(check_method, check_plain)(target)

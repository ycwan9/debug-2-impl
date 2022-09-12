#!/usr/bin/env python3
import os

from check_invar import diff_src
from sample import line_of_interest


def check_cnt(target):
    reduce_expr = tuple(int(i) for i in os.environ["cnt"].split(" "))
    ret = diff_src(target)
    if tuple(len(i) for i in ret) != reduce_expr:
        exit(1)


def check_1st(target):
    from opt_bisect import check_violation
    pass_num = int(os.environ["bisect"])
    if not check_violation(target, pass_num):
        exit(1)


def check_plain(target):
    ret = diff_src(target)
    if not any(ret):
        exit(1)


def check_line(target):
    loi = [int(i) for i in os.environ["loi"].split(" ")]
    orig = [[int(i) for i in l.split(" ") if i] for l in os.environ["violation"].split("\n")]
    ret = diff_src(target, set(loi))
    vios, _ = line_of_interest(ret)
    for i, j in zip(orig[:1], vios):
        assert set(i) == set(j)
    assert orig[1][0] == vios[1][0]


if __name__ == "__main__":
    check_method = os.getenv("REDUCE_METHOD")
    target = os.environ["creduce_target"]
    {
        "1st": check_1st,
        "cnt": check_cnt,
        "line": check_line
    }.get(check_method, check_plain)(target)

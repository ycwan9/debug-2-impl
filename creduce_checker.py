#!/usr/bin/env python3
import os
from subprocess import check_call

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


def check_custom(target, checker):
    ret = diff_src(target)
    import importlib.util as impu
    s = impu.spec_from_file_location("mod", checker)
    mod = impu.module_from_spec(s)
    s.loader.exec_module(mod)
    exit(bool(mod.check(ret)))


def check_line(target):
    loi = [int(i) for i in os.environ["loi"].split(" ")]
    orig = [[int(i) for i in l.split(" ") if i] for l in os.environ["violation"].split("\n")]
    ret = diff_src(target, set(loi))
    vios, _ = line_of_interest(ret)
    for i, j in zip(orig[:3], vios):
        assert set(i) == set(j)
    assert orig[3][0] == vios[3][0]
    assert set(orig[4]) == set(vios[4])


if __name__ == "__main__":
    check_method = os.getenv("REDUCE_METHOD")
    target = os.environ["creduce_target"]
    if not os.getenv("SKIP_CCOMP_REDUCE"):
        check_call(["timeout", "-s", "9", "30", "ccomp", "-interp", "-fall", target])
    custom_checker = os.getenv("CUSTOM_CHECKER")
    if custom_checker:
        check_custom(target, custom_checker)
    else:
        {
            "1st": check_1st,
            "cnt": check_cnt,
            "line": check_line
        }.get(check_method, check_plain)(target)

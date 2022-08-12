#!/usr/bin/env python3
import itertools
import logging
import sys
import subprocess
import re
from subprocess import run, check_output
from record_trace import record
from check_invar import CLANG, CFALGS, CFALGS_OPT, CFALGS_UNOPT, diff_trace


BISECT_OUTPUT_EXP = re.compile(r"BISECT: running pass \(([0-9]+)\)")


def bisect_flag(x: int):
    return ["-mllvm", f"-opt-bisect={x}"]


def bisect_command(fn, fn_o, cnt):
    return [
        CLANG,
        "-o",
        fn_o,
        *bisect_flag(cnt),
        *CFALGS,
        *CFALGS_OPT,
        fn
    ]


def bisect_1st_violation(fn):
    trace_u = original_trace(fn)
    fn_o = f"{fn}.opt.elf"
    l = 0
    r = opt_pass_count(fn, fn_o)
    while l < r:
        mid = (l + r) // 2
        if (any(diff_trace(trace_u, record_bisect(fn, fn_o, mid)))):
            r = mid
        else:
            l = mid + 1
    return l


def check_violation(fn, x: int):
    assert x > 1
    trace_u = original_trace(fn)
    fn_o = f"{fn}.opt.elf"
    return (not any(diff_trace(trace_u, record_bisect(fn, fn_o, x-1)))) \
        and any(diff_trace(trace_u, record_bisect(fn, fn_o, x)))


def original_trace(fn):
    fn_u = f"{fn}.unopt.elf"
    run(bisect_command(fn, fn_u, 0), check=True)
    return record(fn_u)


def opt_pass_count(fn, fn_o):
    """get total pass number of opt bisect"""
    # get pass count
    bisect_passes = check_output(
        bisect_command(fn, fn_o, -1),
        stderr=subprocess.STDOUT,
        check=True)
    return int(BISECT_OUTPUT_EXP.findall(bisect_passes)[-1])


def record_bisect(fn, fn_o, cnt):
    """record trace compiled w/ opt bisect"""
    run(bisect_command(fn, fn_o, cnt), check=True)
    return record(fn_o)

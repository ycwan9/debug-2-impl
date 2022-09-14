#!/usr/bin/env python3
import itertools
import logging
import sys
import subprocess
import re
import os
from subprocess import run, check_output
from record_trace import record
from check_invar import CLANG, CFALGS, CFALGS_OPT, CFALGS_UNOPT, diff_trace


BISECT_OUTPUT_EXP = re.compile(r"BISECT: running pass \(([0-9]+)\)")


def bisect_flag(x: int):
    return ["-mllvm", f"-opt-bisect-limit={x}"]


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
    fn_o = f"{fn}.bi.elf"
    l = 0
    r, o = opt_pass_count(fn, fn_o)
    assert any(diff_trace(trace_u, record_bisect(fn, fn_o, r)))
    while l < r:
        mid = (l + r) // 2
        if (any(diff_trace(trace_u, record_bisect(fn, fn_o, mid)))):
            r = mid
        else:
            l = mid + 1
    p = l
    pat = f"({p})"
    ro = []
    for i in o.split("\n"):
        if i.find(pat) >= 0:
            ro.append(i)
    return p, " ".join(ro)


def check_violation(fn, x: int):
    assert x > 1
    trace_u = original_trace(fn)
    fn_o = f"{fn}.bi.elf"
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
        stderr=subprocess.STDOUT)
    bisect_passes = bisect_passes.decode()
    return int(BISECT_OUTPUT_EXP.findall(bisect_passes)[-1]), bisect_passes


def record_bisect(fn, fn_o, cnt):
    """record trace compiled w/ opt bisect"""
    run(bisect_command(fn, fn_o, cnt), check=True)
    return record(fn_o)


if __name__ == "__main__":
    logging.basicConfig(level=(logging.DEBUG if os.getenv("TRACE_DEBUG") else logging.INFO))
    print(bisect_1st_violation(sys.argv[1]))

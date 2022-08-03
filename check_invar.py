#!/usr/bin/env python3
import itertools
import logging
import sys
from subprocess import run
from record_trace import record


def check_li(trace_u, trace_o):
    """check line invariant"""
    L = lambda t: {i.line for i in t}
    return L(trace_o).difference(L(trace_u))


def check_bi(trace_u, trace_o):
    """check Backtrace Invariant"""
    lines_u = {k: list(g) for k, g in itertools.groupby(
        trace_u, lambda x: x.line)}

    def check_one(t):
        for i in lines_u.get(t.line, []):
            if set(t.bt).issubset(set(i.bt)):
                return False
        return True

    return [i for i in trace_o if check_one(i)]


def check_si(trace_u, trace_o):
    """check Scope Invariant"""
    lines_u = {k: list(g) for k, g in itertools.groupby(
        trace_u, lambda x: x.line)}

    varnames = lambda x: {i.name for i in x.var}

    return list(filter(bool, map(
        lambda x: filter(
            lambda y: not varnames(x).issubset(varnames(y)),
            lines_u.get(x.line, [])
        )
    )))


def check_pi(trace_u, trace_o):
    """check """
    params = lambda x: {(i.name, i.type, i.value) for t in x for i in t.arg}
    return params(trace_o).difference(params(trace_u))


def diff_trace(trace_u, trace_o):
    trace_o.sort(key=lambda x: x.line)
    trace_u.sort(key=lambda x: x.line)
    return tuple(f(trace_u, trace_o) for f in [check_li, check_bi, check_li, check_pi])


def diff_exe(u, o):
    return diff_trace(record(u), record(o))


CFALGS = [
    "-Werror=conditional-uninitialized",
    "-Werror=format-insufficient-args",
    "-Werror=format-pedantic",
    "-Werror=implicit-function-declaration",
    "-Werror=implicit-int",
    "-Werror=incompatible-library-redeclaration",
    "-Werror=incompatible-pointer-types",
    "-Werror=int-conversion",
    "-Werror=pedantic",
    "-Werror=return-type",
    "-Werror=sometimes-uninitialized",
    "-Werror=uninitialized",
    "-Werror=uninitialized-const-reference",
    "-g"
]
CFALGS_UNOPT = ["-O0"]
CFALGS_OPT = ["-O2"]
CLANG = "clang"


def diff_src(fn):
    fn_u = f"{fn}.unopt.elf"
    fn_o = f"{fn}.opt.elf"
    run([CLANG, "-o", fn_u, *CFALGS, *CFALGS_UNOPT, fn], check=True)
    run([CLANG, "-o", fn_o, *CFALGS, *CFALGS_OPT, fn], check=True)
    return diff_exe(fn_u, fn_o)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ret = diff_src(sys.argv[1])
    if any(ret):
        print(ret)
        exit(1)

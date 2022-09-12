#!/usr/bin/env python3
import itertools
import logging
import sys
from subprocess import run
from record_trace import record as lldb_record
from record_gdb import record as gdb_record


def check_li(trace_u, trace_o):
    """check line invariant"""
    raise NotImplementedError
    L = lambda t: {i.line for i in t}
    diff = L(trace_o).difference(L(trace_u))
    if not diff:
        return None
    lines = [i.line for i in trace_o]
    loi = set(diff)
    for i, v in enumerate(lines):
        if v in diff and i > 0:
            loi.add(lines[i-1])
    return diff, loi


IGNORED_BT = {'__libc_start_main', '_start'}


def check_bi(trace_u, trace_o):
    """check Backtrace Invariant"""
    lines_u = {k: list(g) for k, g in itertools.groupby(
        trace_u, lambda x: x.line)}

    def check_one(t):
        for i in lines_u.get(t.line, []):
            if not set(t.bt).symmetric_difference(set(i.bt)).difference(IGNORED_BT):
                return False
        return True

    return [i for i in trace_o if check_one(i)]


def check_si(trace_u, trace_o):
    """check Scope Invariant"""
    raise NotImplementedError
    lines_u = {k: list(g) for k, g in itertools.groupby(
        trace_u, lambda x: x.line)}

    varnames = lambda x: {i.name for i in x.var}

    return [
        (o, u) for o in trace_o for u in lines_u.get(o.line, [])
        if not varnames(o).issubset(varnames(u))
    ]


def check_pi(trace_u, trace_o):
    """check """
    params = lambda x: {(i.name, i.type, i.value) for t in x for i in t.arg}
    violation = params(trace_o).symmetric_difference(params(trace_u))
    varnames = {(i[0], i[1]) for i in violation}
    loi = {t.line for t in trace_u + trace_o if
           varnames.intersection({(i.name, i.type) for i in t.arg})}
    return (violation, loi) if violation else None


def diff_trace(trace_u, trace_o):
    trace_o = [i for i in trace_o if i.line != 0]
    trace_u = [i for i in trace_u if i.line != 0]
    trace_o.sort(key=lambda x: x.line)
    trace_u.sort(key=lambda x: x.line)
    return tuple(f(trace_u, trace_o) for f in [check_bi, check_pi])


def diff_exe(o, loi=None):
    return diff_trace(lldb_record(o, loi), gdb_record(o, loi))


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
    "-Wno-error=strict-prototypes",
    "-g"
]
CFALGS_UNOPT = ["-O0"]
CFALGS_OPT = ["-O2"]
CLANG = "clang"


def diff_src(fn, loi=None):
    fn_u = f"{fn}.unopt.elf"
    fn_o = f"{fn}.opt.elf"
    run([CLANG, "-o", fn_u, *CFALGS, *CFALGS_UNOPT, fn], check=True)
    #run([CLANG, "-o", fn_o, *CFALGS, *CFALGS_OPT, fn], check=True)
    return diff_exe(fn_u)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ret = diff_src(sys.argv[1])
    if any(ret):
        print(ret)
        exit(1)

#!/usr/bin/env python3
import itertools
import logging
import sys
from itertools import chain
from subprocess import run, CalledProcessError

import os
if os.getenv("USE_GDB"):
    from record_gdb import record
else:
    from record_trace import record


import importlib
__flags = importlib.import_module(os.getenv("COMPILE_FLAGS", "default_flags"))
CFALGS = __flags.CFALGS
CFALGS_UNOPT = __flags.CFALGS_UNOPT
CFALGS_OPT = __flags.CFALGS_OPT
CLANG = __flags.CLANG


class TraceException(Exception):
    pass


class CompileException(TraceException):
    pass


class RecordException(TraceException):
    pass


class UnoptimizedTraceException(TraceException):
    pass


class OptimizedTraceException(TraceException):
    pass


class CompileUnoptimizedException(CompileException, UnoptimizedTraceException):
    pass


class CompileOptimizedException(CompileException, OptimizedTraceException):
    pass


class RecordUnoptimizedException(RecordException, UnoptimizedTraceException):
    pass


class RecordOptimizedException(RecordException, OptimizedTraceException):
    pass


def check_li(trace_u, trace_o):
    """check line invariant"""
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

    return [
        (o, u) for o in trace_o for u in lines_u.get(o.line, [])
        if not varnames(o).issubset(varnames(u))
    ]


def check_pi(trace_u, trace_o):
    """check """
    params = lambda x: {(i.name, i.type, i.value) for t in x for i in t.arg}
    violation = params(trace_o).difference(params(trace_u))
    varnames = {(i[0], i[1]) for i in violation}
    loi = {t.line for t in trace_u if varnames
           .intersection({(i.name, i.type) for i in t.arg})}
    return (violation, loi) if violation else None


def check_intermediate(trace_u, trace_o):
    return {i for i in
            (i.intermediate for i in chain(trace_u, trace_o))
            if i}


def no_check(a, b):
    return None


def diff_trace(trace_u, trace_o):
    trace_o = [i for i in trace_o if i.line != 0]
    trace_u = [i for i in trace_u if i.line != 0]
    trace_o.sort(key=lambda x: x.line)
    trace_u.sort(key=lambda x: x.line)
    return tuple(f(trace_u, trace_o) for f in
                 [
                     check_li,
                     check_bi,
                     check_si,
                     check_pi,
                     check_intermediate
                 ])


def diff_exe(u, o, loi=None):
    try:
        tu = record(u, loi)
    except Exception as e:
        raise RecordUnoptimizedException from e
    try:
        to = record(o, loi)
    except Exception as e:
        raise RecordOptimizedException from e
    return diff_trace(tu, to)


def diff_src(fn, loi=None):
    fn_u = f"{fn}.unopt.elf"
    fn_o = f"{fn}.opt.elf"
    try:
        run([CLANG, "-o", fn_u, *CFALGS, *CFALGS_UNOPT, fn], check=True)
    except CalledProcessError as e:
        raise CompileUnoptimizedException from e
    try:
        run([CLANG, "-o", fn_o, *CFALGS, *CFALGS_OPT, fn], check=True)
    except CalledProcessError as e:
        raise CompileOptimizedException from e
    return diff_exe(fn_u, fn_o)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ret = diff_src(sys.argv[1])
    if any(ret):
        print(ret)
        exit(1)

#!/usr/bin/env python3
# usage: <self> <binary>
import sys
import os
import logging
import pickle

sys.path.append(".")

import gdb
from gdb.FrameDecorator import FrameDecorator

from record_trace import Var, TraceItem, accept_types

logger = logging.getLogger(__file__)

def __filter_out_none(l):
    return [i for i in l if i is not None]


def parse_var(x):
    name = x.sym.name
    tp = x.sym.type.name
    if tp not in accept_types:
        return
    v = x.sym.value(gdb.newest_frame()).format_string()
    try:
        v = int(v)
    except ValueError:
        return
    return Var(name, tp, v)


def collect_step():
    line_no = gdb.find_pc_line(gdb.newest_frame().pc()).line

    d = FrameDecorator(gdb.newest_frame())
    arg = __filter_out_none([parse_var(i) for i in d.frame_args()])
    local = __filter_out_none([parse_var(i) for i in d.frame_locals()])

    bt = []
    f = gdb.newest_frame()
    while f:
        bt.append(f.name())
        f = f.older()

    return TraceItem(
        line_no,
        local,
        bt,
        arg
    )


def record(savpos=None, line_of_interest=None):
    gdb.execute("start")
    thread = gdb.selected_thread()
    source_file = FrameDecorator(gdb.newest_frame()).filename()
    trace = []
    if line_of_interest:
        for i in set(line_of_interest):
            gdb.execute(f"b {i}")
        while thread.is_valid() and thread.is_stopped():
            logger.debug("frame: %s", gdb.newest_frame().name())
            if FrameDecorator(gdb.newest_frame()).filename() == source_file:
                trace.append(collect_step())
            gdb.execute("s")
            logger.debug("frame: %s", gdb.newest_frame().name())
            if FrameDecorator(gdb.newest_frame()).filename() == source_file:
                trace.append(collect_step())
            gdb.execute("c")
    else:
        while thread.is_valid() and thread.is_stopped():
            logger.debug("frame: %s", gdb.newest_frame().name())
            if FrameDecorator(gdb.newest_frame()).filename() == source_file:
                trace.append(collect_step())
            gdb.execute("s")
    if savpos:
        pickle.dump(trace, open(savpos, "wb"))
    return trace

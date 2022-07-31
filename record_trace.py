#!/usr/bin/env python3
# usage: <self> <binary>
import sys
import lldb
import os
import logging
from dataclasses import dataclass


logger = logging.getLogger(__file__)
accept_types = {"int", "short", "unsigned short", "unsigned int"}


@dataclass
class Var:
    name: str
    type: str
    value: str


@dataclass
class TraceItem:
    line: int
    var: list
    bt: list
    arg: list


def collect_step(thread):
    frame = thread.GetFrameAtIndex(0)
    line_no = frame.line_entry.line

    def parse_var(var):
        ignores = ["*", "[", "out of scope", "not available", "optimized out"]
        for i in ignores:
            if i in var.__str__():
                return
        var_name = var.__str__().split(")")[-1].split("=")[0].strip()
        var_value = var.__str__().split(")")[-1].split("=")[-1].strip()
        var_type = var.GetType().GetCanonicalType().__str__().strip()
        if var_type in accept_types:
            return Var(var_name, var_type, var_value)

    return TraceItem(
        line_no,
        [i for i in [parse_var(v) for v in frame.get_locals()] if i],
        [str(thread.GetFrameAtIndex(i).name) for i in range(thread.num_frames)],
        [i for i in [parse_var(v) for v in frame.get_arguments()] if i],
    )


def record(exe):

    debugger = lldb.SBDebugger.Create()
    debugger.SetAsync(False)
    target = debugger.CreateTargetWithFileAndArch(exe, "x86_64")
    if not target:
        raise Exception("invalid target")
    assert target.IsValid()

    # b main
    bp = target.BreakpointCreateByName("main")
    if not bp:
        raise Exception("fail to break at main")
    # run
    process = target.LaunchSimple(None, None, os.getcwd())
    # hit bp
    assert process.GetState() == lldb.eStateStopped

    thread = process.GetThreadAtIndex(0)

    source_file = target.FindFunctions("main")[0].compile_unit.file
    trace = []
    while process.GetState() == lldb.eStateStopped:
        logger.debug("frame: %s", thread.GetFrameAtIndex(0))
        if thread.GetFrameAtIndex(0).line_entry.file == source_file:
            trace.append(collect_step(thread))
        thread.StepInto()
    return trace


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    trace = record(sys.argv[1])
    print(trace)

#!/usr/bin/env python3
# usage: <self> <binary>
import sys
import lldb
import json
import os
import logging


logger = logging.getLogger(__file__)
accept_types = {"int", "short", "unsigned short", "unsigned int"}


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
            return {
                "name": var_name,
                "type": var_type,
                "value": var_value
            }

    return {
        "line": line_no,
        "var": [i for i in [parse_var(v) for v in frame.get_locals()] if i],
        "bt": [str(thread.GetFrameAtIndex(i).name) for i in range(thread.num_frames)],
        "arg": [i for i in [parse_var(v) for v in frame.get_arguments()] if i],
    }


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

    source_file = thread.GetFrameAtIndex(0).line_entry.file
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
    print(json.dumps(trace))

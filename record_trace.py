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
        [i.name for i in thread.get_thread_frames()],
        [i for i in [parse_var(v) for v in frame.get_arguments()] if i],
    )


def get_main_line(fn: str):
    """find line of main function
    in order to avoid lldb bug"""
    with open(fn) as f:
        it = iter(f)
        for no, line in enumerate(it):
            if line.find("int main") != -1:
                if line.find("{") != -1:
                    return no + 1
                else:
                    try:
                        if next(it).find("{") != -1:
                            return no + 2
                    except StopIteration:
                        pass


def record(exe, line_of_interest=None):

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

    main_line = get_main_line(source_file.fullpath)

    def pos_valid():
        le = thread.GetFrameAtIndex(0).line_entry
        return le.file == source_file and le.line != main_line

    if line_of_interest:
        for i in set(line_of_interest):
            target.BreakpointCreateByLocation(source_file, i)
        while process.GetState() == lldb.eStateStopped:
            logger.debug("frame: %s", thread.GetFrameAtIndex(0))
            if pos_valid():
                trace.append(collect_step(thread))
            thread.StepInto()
            logger.debug("frame: %s", thread.GetFrameAtIndex(0))
            if pos_valid():
                trace.append(collect_step(thread))
            process.Continue()
    else:
        while process.GetState() == lldb.eStateStopped:
            logger.debug("frame: %s", thread.GetFrameAtIndex(0))
            if pos_valid():
                trace.append(collect_step(thread))
            thread.StepInto()
    return trace


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    trace = record(sys.argv[1])
    print(trace)

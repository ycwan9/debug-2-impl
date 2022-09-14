#!/usr/bin/env python3
# usage: <self> <binary>
import sys
import lldb
import os
import logging
import re
from dataclasses import dataclass


logger = logging.getLogger(__file__)
accept_types = {"int8_t", "int", "short", "unsigned short", "unsigned int"}
alternative_types = {
    "int16_t": "short",
    "int32_t": "int",
    "uint16_t": "unsigned short",
    "uint32_t": "unsigned int"
}


def decor_type(x: str):
    if not x:
        return
    if x.startswith("const "):
        x = x[6:]
    x = alternative_types.get(x, x)
    if x in accept_types:
        return x


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
    intermediate: tuple


def collect_step(thread):
    frame = thread.GetFrameAtIndex(0)
    line_no = frame.line_entry.line

    def parse_var(var):
        ignores = ["*", "[", "out of scope", "not available", "optimized out", "DW_OP_entry_value"]
        for i in ignores:
            if i in var.__str__():
                return
        var_name = var.__str__().split(")")[-1].split("=")[0].strip()
        if not var_name:
            return
        var_value = var.__str__().split(")")[-1].split("=")[-1].strip()
        var_type = var.GetType().GetCanonicalType().__str__().strip()
        var_type = decor_type(var_type)
        try:
            var_value = int(var_value)
        except ValueError:
            return
        if var_type:
            return Var(var_name, var_type, var_value)

    return (
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

    with open(source_file.fullpath) as f:
        src = list(f)

    intermediate_exp = re.compile("(t[0-9]+) = (.+);")

    ci = debugger.GetCommandInterpreter()
    assert ci
    res = lldb.SBCommandReturnObject()

    def check_intermediate():
        line_no = thread.GetFrameAtIndex(0).line_entry.line
        r = intermediate_exp.search(src[line_no - 1])
        thread.StepInto()
        if not r:
            return
        v, e = r.groups()
        ci.HandleCommand(f"p {v} ^ ({e})", res)
        if res.Succeeded():
            o = res.GetOutput()
            logger.debug("p %s, %s => %s", v, e, o)
            if o.find("= 0") < 0:
                return line_no, v, e, o

    def check_step():
        s = collect_step(thread)
        i = check_intermediate()
        return TraceItem(*s, i)

    def pos_valid():
        le = thread.GetFrameAtIndex(0).line_entry
        return le.file == source_file and le.line != main_line

    if line_of_interest:
        for i in set(line_of_interest):
            target.BreakpointCreateByLocation(source_file, i)
        while process.GetState() == lldb.eStateStopped:
            logger.debug("frame: %s", thread.GetFrameAtIndex(0))
            if pos_valid():
                trace.append(check_step())
            if thread.GetFrameAtIndex(0).line_entry.line not in line_of_interest:
                process.Continue()
    else:
        while process.GetState() == lldb.eStateStopped:
            logger.debug("frame: %s", thread.GetFrameAtIndex(0))
            if pos_valid():
                trace.append(check_step())
            else:
                thread.StepInto()
    return trace


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    trace = record(sys.argv[1])
    print(trace)

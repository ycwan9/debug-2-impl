#!/usr/bin/env python3
# usage: <self> <binary>
import sys
import os
import logging
import pickle
import uuid
from subprocess import run

from record_trace import Var, TraceItem, accept_types

logger = logging.getLogger(__file__)

def record(exe, line_of_interest=None):
    savpos = f"{exe}.{uuid.uuid4()}.trace.pickle"
    cmd = [
        *"gdb -batch".split(" "),
        "-ex", "source record_gdb_inner.py",
        "-ex", "python record({}, {})".format(repr(savpos), repr(line_of_interest)),
        exe
    ]
    run(cmd, check=True)

    trace = pickle.load(open(savpos, "rb"))
    os.unlink(savpos)
    return trace

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    trace = record(sys.argv[1])
    print(trace)

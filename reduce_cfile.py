#!/usr/bin/env python3
import sys
import logging
import os
import shutil
from subprocess import run


def reduce_file(srcfile):
    cfile = os.path.abspath(srcfile + ".creduce.c")
    shutil.copyfile(srcfile, cfile)
    os.environ["creduce_target"] = os.path.basename(cfile)
    checker = os.path.dirname(os.path.abspath(__file__)) + "/creduce_checker.py"
    run(["creduce", checker, cfile], cwd=os.path.dirname(cfile), check=True)


if __name__ == "__main__":
    logging.basicConfig(level=(logging.DEBUG if os.getenv("TRACE_DEBUG") else logging.INFO))
    reduce_file(sys.argv[1])

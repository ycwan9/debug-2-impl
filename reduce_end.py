#!/usr/bin/env python3
import sys
import logging
import os
import shutil
from subprocess import run


script_path = os.path.dirname(os.path.abspath(__file__))


def reduce_command(cfile):
    checker = script_path + "/creduce_checker.py"
    return ["creduce", checker, cfile]


def reduce_file(srcfile):
    cfile = os.path.abspath(srcfile + ".creduce.c")
    shutil.copyfile(srcfile, cfile)
    os.environ["creduce_target"] = os.path.basename(cfile)
    run(reduce_command(cfile), cwd=os.path.dirname(cfile), check=True)


if __name__ == "__main__":
    logging.basicConfig(level=(logging.DEBUG if os.getenv("TRACE_DEBUG") else logging.INFO))
    reduce_file(sys.argv[1])

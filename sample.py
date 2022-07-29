#!/usr/bin/env python3
import sys
import logging
import os
import shutil
from subprocess import run

import gencsmith
from check_invar import diff_src


def reduce_file(srcfile):
    cfile = os.path.abspath(srcfile + ".creduce.c")
    shutil.copyfile(srcfile, cfile)
    os.environ["creduce_target"] = cfile
    checker = os.path.dirname(os.path.abspath(__file__)) + "/creduce_checker.py"
    run(["creduce", checker, cfile], cwd=os.path.dirname(cfile), check=True)


def main():
    if not os.getenv("C_INCLUDE_PATH"):
        os.environ["C_INCLUDE_PATH"] = "/usr/include/csmith"
    cfile = sys.argv[1]
    gencsmith.gencsmith(cfile)
    ret = diff_src(sys.argv[1])
    if any(ret):
        print("violation found")
        reduce_file(cfile)
        print(ret)
    else:
        exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=(logging.DEBUG if os.getenv("TRACE_DEBUG") else logging.INFO))
    main()

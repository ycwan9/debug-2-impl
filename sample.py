#!/usr/bin/env python3
import sys
import logging
import os
import shutil
from subprocess import run

import gencsmith
from check_invar import diff_src
from reduce_cfile import reduce_file


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

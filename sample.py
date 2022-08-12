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
    if not os.getenv("SKIP_CSMITH"):
        gencsmith.gencsmith(cfile)
    ret = diff_src(cfile)
    if any(ret):
        check_method = os.getenv("REDUCE_METHOD")
        reduce_expr = ""
        if check_method == "1st":
            from opt_bisect import bisect_1st_violation
            reduce_expr = str(bisect_1st_violation(cfile))
        elif check_method == "cnt":
            reduce_expr = " ".join(str(len(i)) for i in ret)
        os.environ["reduce_expr"] = reduce_expr
        print("violation found")
        reduce_file(cfile)
        print(ret)
    else:
        exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=(logging.DEBUG if os.getenv("TRACE_DEBUG") else logging.INFO))
    main()

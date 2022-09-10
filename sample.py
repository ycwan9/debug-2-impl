#!/usr/bin/env python3
import sys
import logging
import os
import shutil
from subprocess import run

import gencsmith
from check_invar import diff_src
from reduce_cfile import reduce_file
from transform import random_transform


def main():
    if not os.getenv("C_INCLUDE_PATH"):
        os.environ["C_INCLUDE_PATH"] = "/usr/include/csmith"
    cfile = sys.argv[1]
    if not os.getenv("SKIP_CSMITH"):
        gencsmith.gencsmith(cfile)
    if os.getenv("DO_TRANSFORM"):
        random_transform(cfile)
        assert gencsmith.checkUB(cfile) == 0
    ret = diff_src(cfile)
    if any(ret):
        check_method = os.getenv("REDUCE_METHOD")
        if check_method == "1st":
            from opt_bisect import bisect_1st_violation
            os.environ["bisect"] = str(bisect_1st_violation(cfile))
        elif check_method == "line":
            vios, loi = line_of_interest(ret)
            os.environ["loi"] = " ".join(map(str, loi))
            os.environ["violation"] = "\n".join(
                " ".join(map(str, i)) for i in vios)
        print("violation found")
        print(ret)
        if not os.getenv("SKIP_REDUCE"):
            reduce_file(cfile)
        print(ret)
    else:
        exit(33)


def line_of_interest(r):
    l, b, s, p = r
    vios = (
        l[0] if l else [],
        [i.line for i in b],
        [o.line for o, u in s],
        [len(p[0]) if p else 0]
    )
    loi = set(l[1] if l else [])\
        .union(set(vios[1]))\
        .union(set(vios[2]))\
        .union(p[1] if p else set())
    return vios, loi


if __name__ == "__main__":
    logging.basicConfig(level=(logging.DEBUG if os.getenv("TRACE_DEBUG") else logging.INFO))
    main()

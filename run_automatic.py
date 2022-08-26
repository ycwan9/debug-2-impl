#!/usr/bin/env python3
# usage: <self> <savedir> <genfile> <cycle> <trans per cycle>
import sys
import logging
import os
import shutil
from datetime import datetime
from subprocess import run

savedir, gendir = sys.argv[1:3]
gencnt, trancnt = map(int, sys.argv[3:5])


def test(prefix=""):
    ret = run(["python3", "sample.py", f"{gendir}/sample.c"]).returncode
    if ret == 0:
        bugdir = "{}/{}_{}".format(savedir, prefix, datetime.now().isoformat())
        os.mkdir(bugdir)
        os.system(f"bash -c 'cp -a {gendir}/{{*.c,perses*}} {bugdir}'")
        os.system(f"bash -c 'rm -r {gendir}/{{*.c,perses*}}'")
    return ret


for i in range(gencnt):
    # generate valid test file
    os.environ["SKIP_CSMITH"] = ""
    os.environ["DO_TRANSFORM"] = ""
    while test(f"gen.{i:03d}") not in (0, 33):
        pass

    os.environ["SKIP_CSMITH"] = "1"
    os.environ["DO_TRANSFORM"] = "1"
    for j in range(trancnt):
        test(f"gen.{i:03d}.{j:03d}")

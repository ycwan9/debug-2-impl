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
    with open(f"{gendir}/stdout.log", "wb") as f:
        ret = run(
            ["python3", "sample.py", f"{gendir}/sample.c"],
            stdout=f
        ).returncode
    if ret in (0, 34):
        bugdir = "{}/{}_{}_{}".format(
            savedir,
            prefix,
            "err" if ret == 34 else "vio",
            datetime.now().isoformat())
        os.mkdir(bugdir)
        os.system(f"bash -c 'cp -a {gendir}/{{*.c,*.log,perses*}} {bugdir}'")
        os.system(f"bash -c 'rm -r {gendir}/{{*.*.c,*.log,*.orig,perses*}}'")
    return ret


for i in range(gencnt):
    # generate valid test file
    os.environ["SKIP_CSMITH"] = ""
    os.environ["DO_TRANSFORM"] = ""
    os.environ["RUN_COUNT"] = f"{i:03d}"
    while test(f"gen.{i:03d}") != 33:
        pass

    os.environ["SKIP_CSMITH"] = "1"
    os.environ["DO_TRANSFORM"] = "1"
    for j in range(trancnt):
        test(f"gen.{i:03d}.{j:03d}")

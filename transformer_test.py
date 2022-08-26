#!/usr/bin/env python3
# usage: <self> <savedir> <genfile> <cycle> <trans per cycle>
import sys
import logging
import os
import shutil
from subprocess import run

checkdst, genfile = sys.argv[1:3]
gencnt, trancnt = map(int, sys.argv[3:5])

os.environ["SKIP_REDUCE"] = "1"

for i in range(gencnt):
    # generate valid test file
    os.environ["SKIP_CSMITH"] = ""
    os.environ["DO_TRANSFORM"] = ""
    while run(["python3", "sample.py", genfile]).returncode != 33:
        pass
    shutil.copyfile(genfile, f"{checkdst}/gen.{i:03d}.c")

    os.environ["SKIP_CSMITH"] = "1"
    os.environ["DO_TRANSFORM"] = "1"
    transfile = f"{genfile}.trans.c"
    for j in range(trancnt):
        ret = run(["python3", "sample.py", genfile]).returncode
        if ret == 0:
            shutil.copyfile(transfile, f"{checkdst}/gen.{i:03d}.tran.{j:03d}.c")
        elif ret != 33:
            shutil.copyfile(transfile, f"{checkdst}/gen.{i:03d}.err.{j:03d}.c")

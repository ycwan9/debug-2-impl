#!/usr/bin/env python3
import sys
import logging
import os
import shutil
import random
from subprocess import run

MAX_TRANS = int(os.getenv("MAX_TRANS", "4"))

TRANSFORMERS = [
    list(i.split(" ")) for i in [
        "three_addr_transformer -t .1 -extra-arg=-Wno-error=extra-semi",
        "random_attributes -t .1",
        "random_format"
    ]
]


def transform(transformer: list, fin: str):
    forig = f"{fin}.orig.c"
    shutil.move(fin, forig)
    run([
        *transformer,
        "-p",
        os.path.dirname(fin),
        "-o",
        fin,
        forig
    ],
        check=True)


def random_transform(fin: str):
    trans = list(TRANSFORMERS)
    random.shuffle(trans)
    trans = trans[:random.randint(0, len(trans))]
    for i in trans:
        transform(i, fin)

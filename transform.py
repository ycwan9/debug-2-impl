#!/usr/bin/env python3
import sys
import logging
import os
import shutil
import random
from subprocess import run

MAX_TRANS = int(os.getenv("MAX_TRANS", "5"))

TRANSFORMERS = [
    list(i.split(" ")) for i in [
        "three_addr_transformer -t .2",
        "random_attributes -t .5",
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
    trans = [random.choice(TRANSFORMERS) for _ in random.randint(0, MAX_TRANS)]
    for i in trans:
        transform(i, fin)

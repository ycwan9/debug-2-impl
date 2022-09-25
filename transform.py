#!/usr/bin/env python3
import logging
import os
import random
from subprocess import run

logger = logging.getLogger(__file__)
MAX_TRANS = int(os.getenv("MAX_TRANS", "4"))

TRANSFORMERS = [
    list(i.split(" ")) for i in [
        "three_addr_transformer -t .5 -extra-arg=-Wno-error=extra-semi",
        "random_attributes -t .1",
        "random_format"
    ]
]


def transform(transformer: list, fin: str, fout: str):
    env = os.environ
    env["C_INCLUDE_PATH"] = os.getenv("TRANS_INCLUDE_PATH", "") + ":" + os.getenv("C_INCLUDE_PATH", "")
    cmd = [
        *transformer,
        "-p",
        os.path.dirname(fin),
        "-o",
        fout,
        fin
    ]
    logger.info("appling %s", str(cmd))
    run(cmd, env=env, check=True)


def random_transform(fin: str, fout: str):
    trans = [i for i in TRANSFORMERS if random.random() >= .5]
    for i in trans:
        transform(i, fin, fout)

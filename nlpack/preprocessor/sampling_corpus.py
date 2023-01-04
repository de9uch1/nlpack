#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import shutil
import subprocess
from io import TextIOWrapper
from typing import Dict, List, Set

import numpy as np

from nlpack import cli


def count_lines(fname: str) -> int:
    if shutil.which("wc"):
        return int(
            subprocess.run(["wc", "-l", fname], capture_output=True, text=True)
            .stdout.strip()
            .split(maxsplit=2)[0]
        )
    else:
        with open(fname, mode="r") as f:
            return len(f.readlines())


def sample_on_memory(
    f_in: TextIOWrapper, f_out: TextIOWrapper, sample_ids: List[int]
) -> None:
    lines = f_in.readlines()
    f_out.writelines([lines[i] for i in sample_ids])


def sample_hash(
    f_in: TextIOWrapper, f_out: TextIOWrapper, sample_ids: List[int]
) -> None:
    samples: Dict[int, str] = dict.fromkeys(sample_ids)
    unseen: Set[int] = set(sample_ids)
    for i, line in enumerate(f_in):
        if i in unseen:
            samples[i] = line
            unseen.remove(i)
            if len(unseen) == 0:
                break
    f_out.writelines(samples.values())


# fmt: off
@cli.subcommand("sampling-corpus")
@cli.option("--input-prefix", "-i", type=str, metavar="PREFIX", required=True,
            help="Input files prefix.")
@cli.option("--output-prefix", "-o", type=str, metavar="PREFIX", required=True,
            help="Output files prefix.")
@cli.option("--suffixes", "-s", multiple=True, metavar="SUFFIXES", required=True,
            help="File suffixes.")
@cli.option("--sampling-size", "-n", type=int, metavar="N", required=True,
            help="Sampling size.")
@cli.option("--on-memory", is_flag=True,
            help="Load all data on memory.")
@cli.option("--seed", type=int, metavar="N", default=0,
            help="Random seed.")
# fmt: on
def sampling_corpus(
    input_prefix: str,
    output_prefix: str,
    suffixes: List[str],
    sampling_size: int,
    on_memory: bool = False,
    seed: int = 0,
):
    """Sampling lines from corpus."""

    fname = input_prefix + "." + suffixes[0]
    num_sentences = count_lines(fname)

    np.random.seed(seed)
    size = min(sampling_size, num_sentences)
    sample_ids = np.random.permutation(num_sentences)[:size].tolist()
    for suffix in suffixes:
        with open(input_prefix + "." + suffix, mode="r") as f_in:
            with open(output_prefix + "." + suffix, mode="w") as f_out:
                if on_memory:
                    sample_on_memory(f_in, f_out, sample_ids)
                else:
                    sample_hash(f_in, f_out, sample_ids)


if __name__ == "__main__":
    sampling_corpus()

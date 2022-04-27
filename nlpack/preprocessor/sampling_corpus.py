#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

import numpy as np

from nlpack import cli


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
@cli.option("--seed", type=int, metavar="N", default=0,
            help="Random seed.")
# fmt: on
def sampling_corpus(
    input_prefix: str,
    output_prefix: str,
    suffixes: List[str],
    sampling_size: int,
    seed: int = 0,
):
    """Sampling lines from corpus."""

    with open(input_prefix + "." + suffixes[0], mode="r") as f_in:
        num_sentences = len(f_in.readlines())

    np.random.seed(seed)
    sampler = np.random.permutation(num_sentences)[:sampling_size]
    for suffix in suffixes:
        with open(input_prefix + "." + suffix, mode="r") as f_in:
            with open(output_prefix + "." + suffix, mode="w") as f_out:
                lines = f_in.readlines()
                samples = [lines[i] for i in sampler]
                f_out.writelines(samples)


if __name__ == "__main__":
    sampling_corpus()

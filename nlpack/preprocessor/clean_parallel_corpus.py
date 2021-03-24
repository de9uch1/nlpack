#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import itertools

from nlpack import cli
from nlpack.tokenizer import Tokenizer


# fmt: off
@cli.subcommand("parallel-cleaner")
@cli.option("--input-prefix", "-i", type=str, metavar="PREFIX", required=True,
            help="Input files prefix.")
@cli.option("--output-prefix", "-o", type=str, metavar="PREFIX", required=True,
            help="Output files prefix.")
@cli.option("--src", "-s", type=str, metavar="SRC", required=True,
            help="Source file suffix.")
@cli.option("--tgt", "-t", type=str, metavar="TGT", required=True,
            help="Target file suffix.")
@cli.option("--min-len", "--min", type=int, metavar="N", default=1,
            help="Minimum sentence length.")
@cli.option("--max-len", "--max", type=int, metavar="N", default=10000,
            help="Maximum sentence length.")
@cli.option("--ratio", type=float, metavar="RATIO", default=9,
            help="Sentence length ratio.")
@cli.option("--label-suffix", "-l", multiple=True, metavar="SUFFIX",
            help="Additional label file extention. It can be specify multiple times.")
# fmt: on
def clean_parallel_corpus(
    input_prefix,
    output_prefix,
    src,
    tgt,
    min_len,
    max_len,
    ratio,
    label_suffix,
):
    """Parallel corpus cleaner."""

    space_tokenizer = Tokenizer("space").tokenize_line

    src_input_path = "{}.{}".format(input_prefix, src)
    tgt_input_path = "{}.{}".format(input_prefix, tgt)
    src_output_path = "{}.{}".format(output_prefix, src)
    tgt_output_path = "{}.{}".format(output_prefix, tgt)

    label_inputs, label_outputs = [], []
    if len(label_suffix) == 0:
        label_inputs.append(itertools.cycle([None]))
        label_outputs.append(itertools.cycle([None]))
    else:
        for label in label_suffix:
            label_inputs.append(open("{}.{}".format(input_prefix, label), mode="r"))
            label_outputs.append(open("{}.{}".format(output_prefix, label), mode="w"))

    num_keep, total_lines = 0, 0
    with open(src_input_path, mode="r") as src_in:
        with open(tgt_input_path, mode="r") as tgt_in:
            with open(src_output_path, mode="w") as src_out:
                with open(tgt_output_path, mode="w") as tgt_out:
                    for src_line, tgt_line, *label_lines in zip(
                        src_in, tgt_in, *label_inputs
                    ):
                        total_lines += 1
                        src_len = len(space_tokenizer(src_line))
                        tgt_len = len(space_tokenizer(tgt_line))
                        if (
                            src_len > max_len
                            or tgt_len > max_len
                            or src_len < min_len
                            or tgt_len < min_len
                            or src_len / tgt_len > ratio
                            or tgt_len / src_len > ratio
                        ):
                            continue
                        src_out.write(src_line)
                        tgt_out.write(tgt_line)
                        if len(label_suffix) > 0:
                            for label_line, label_out in zip(
                                label_lines, label_outputs
                            ):
                                label_out.write(label_line)
                        num_keep += 1

    if len(label_suffix) > 0:
        for label_in, label_out in zip(label_inputs, label_outputs):
            label_in.close()
            label_out.close()

    cli.echo(
        "input sentences: {:,}, output sentences: {:,}".format(total_lines, num_keep),
        err=True,
    )


if __name__ == "__main__":
    clean_parallel_corpus()

#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from nlpack import cli
from nlpack.tokenizer import Tokenizer


# fmt: off
@cli.subcommand("mono-cleaner")
@cli.option("--input-prefix", "-i", type=str, metavar="PREFIX", required=True,
            help="Input files prefix.")
@cli.option("--output-prefix", "-o", type=str, metavar="PREFIX", required=True,
            help="Output files prefix.")
@cli.option("--src", "-s", type=str, metavar="SRC", required=True,
            help="Source file suffix.")
@cli.option("--min-len", "--min", type=int, metavar="N", default=1,
            help="Minimum sentence length.")
@cli.option("--max-len", "--max", type=int, metavar="N", default=10000,
            help="Maximum sentence length.")
# fmt: on
def clean_mono_corpus(
    input_prefix,
    output_prefix,
    src,
    min_len,
    max_len,
):
    """Monolingual corpus cleaner."""

    space_tokenizer = Tokenizer("space").tokenize_line

    src_input_path = "{}.{}".format(input_prefix, src)
    src_output_path = "{}.{}".format(output_prefix, src)

    num_keep, total_lines = 0, 0
    with open(src_input_path, mode="r") as src_in:
        with open(src_output_path, mode="w") as src_out:
            for src_line in src_in:
                total_lines += 1
                src_len = len(space_tokenizer(src_line))
                if src_len > max_len or src_len < min_len:
                    continue
                src_out.write(src_line)
                num_keep += 1

    cli.echo(
        "input sentences: {:,}, output sentences: {:,}".format(total_lines, num_keep),
        err=True,
    )


if __name__ == "__main__":
    clean_mono_corpus()

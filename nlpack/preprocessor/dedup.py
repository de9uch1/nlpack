#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from nlpack import cli


# fmt: off
@cli.subcommand("dedup")
@cli.option("--input-prefix", "-i", type=str, metavar="PREFIX", required=True,
            help="Input files prefix.")
@cli.option("--output-prefix", "-o", type=str, metavar="PREFIX", required=True,
            help="Output files prefix.")
@cli.option("--suffixes", "-s", multiple=True, metavar="SUFFIXES", required=True,
            help="File suffixes.")
# fmt: on
def dedup(input_prefix: str, output_prefix: str, suffixes: List[str]):
    """Deduplicate."""

    lines = []
    for suffix in suffixes:
        with open(input_prefix + "." + suffix, mode="r") as f_in:
            lines.append(f_in.readlines())
    union_lines = dict.fromkeys(tuple(zip(*lines))).keys()
    for suffix, lines_f in zip(suffixes, zip(*union_lines)):
        with open(output_prefix + "." + suffix, mode="w") as f_out:
            f_out.writelines(lines_f)
    cli.echo(
        "input sentences: {:,}, output sentences: {:,}".format(
            len(lines[0]), len(union_lines)
        ),
        err=True,
    )


if __name__ == "__main__":
    dedup()

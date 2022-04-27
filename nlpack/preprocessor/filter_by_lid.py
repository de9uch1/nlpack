#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import urllib.request
from typing import List

from fasttext import load_model

from nlpack import cli
from nlpack.locations import cache_dir

LID_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
LID_FILENAME = "lid.176.bin"


# fmt: off
@cli.subcommand("filter-by-lid")
@cli.option("--input-prefix", "-i", type=str, metavar="PREFIX", required=True,
            help="Input files prefix.")
@cli.option("--output-prefix", "-o", type=str, metavar="PREFIX", required=True,
            help="Output files prefix.")
@cli.option("--suffixes", "-s", multiple=True, metavar="SUFFIXES", required=True,
            help="File suffixes.")
@cli.option("--langs", "-l", multiple=True, metavar="LANGS", required=True,
            help="Languages specified by ISO 639-1. The ignored part is specified by `__`.")
# fmt: on
def filter_by_lid(
    input_prefix: str,
    output_prefix: str,
    suffixes: List[str],
    langs: List[str],
):
    """
    Filters by language identificaion.
    """
    assert len(langs) == len(suffixes)

    fasttext_cache_dir = cache_dir("fasttext")
    lid_model_path = os.path.join(fasttext_cache_dir, LID_FILENAME)
    if not os.path.exists(lid_model_path):
        os.makedirs(fasttext_cache_dir, exist_ok=True)
        cli.echo(
            "Download the language identification model from {} to {}".format(
                LID_URL, lid_model_path
            ),
            err=True,
        )
        urllib.request.urlretrieve(LID_URL, lid_model_path)
        cli.echo("Done", err=True)
    assert os.path.exists(lid_model_path)
    lid_model = load_model(lid_model_path)

    input_files = [open(input_prefix + "." + suffix, mode="r") for suffix in suffixes]
    output_files = [open(output_prefix + "." + suffix, mode="w") for suffix in suffixes]

    lang_labels = ["__label__" + lang if lang != "__" else None for lang in langs]

    num_keep, total_lines = 0, 0
    for each_line in zip(*input_files):
        total_lines += 1
        if all(
            [
                lid_model.predict(line.rstrip())[0][0] == lang_label
                for line, lang_label in zip(each_line, lang_labels)
                if lang_label is not None
            ]
        ):
            for f, line in zip(output_files, each_line):
                f.write(line)
            num_keep += 1

    for f in input_files:
        f.close()
    for f in output_files:
        f.close()

    cli.echo(
        "input sentences: {:,}, output sentences: {:,}".format(total_lines, num_keep),
        err=True,
    )


if __name__ == "__main__":
    filter_by_lid()

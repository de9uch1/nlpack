# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sys
from typing import Any, Dict, List, Optional

from nlpack import cli, utils
from nlpack.normalizer import Normalizer


class Tokenizer:
    def __init__(self, tokenizer_name: str = "space", **tokenizer_kwargs):
        self.tokenizer = None
        if tokenizer_name == "space":
            self.tokenizer = self.space
        if tokenizer_name == "moses":
            try:
                import sacremoses
            except ImportError:
                cli.abort("Please install sacremoses with: pip install sacremoses")

            lang = tokenizer_kwargs.get("lang", "en")
            self.hypen_split = tokenizer_kwargs.get("hyphen_split", False)
            self.moses_tokenizer = sacremoses.Tokenizer(lang=lang)

            self.tokenizer = self.moses

    def __call__(self, lines: List[str]):
        return self.tokenizer(lines)

    def tokenize_line(self, line: str):
        return self.tokenizer([line])[0]

    def space(self, lines: List[str]):
        return [Normalizer.space(line).split(" ") for line in lines]

    def moses(self, lines: List[str]):
        return self.moses_tokenizer.tokenize(
            lines, aggresive_dash_splits=self.hypen_split
        )


# fmt: off
@cli.subcommand("tokenizer")
@cli.option("--type", "-t", "type", metavar="TYPE", default="space",
            choice=["space", "moses"])
# fmt: on
def tokenize(type):
    """Text tokenizer

    Text is read from standard input.

    \f

    Args:
        type: (str): Tokenizer type.
    """
    tokenizer = Tokenizer(type)
    for lines in utils.buffer_lines(sys.stdin):
        lines = tokenizer(lines.lines)
        print("\n".join(lines))


if __name__ == "__main__":
    tokenize()

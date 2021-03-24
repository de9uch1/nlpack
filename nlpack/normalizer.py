#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import re
import sys
import unicodedata

from nlpack import cli

SPACE_NORM = re.compile(r"\s+")
Z2H_TABLE = {
    "　": " ",
    "，": ",",
    "．": ".",
    "：": ":",
    "；": ";",
    "？": "?",
    "！": "!",
    "゛": '"',
    "´": "'",
    "｀": "`",
    "＾": "^",
    "＿": "_",
    "—": "-",
    "‐": "-",
    "／": "/",
    "＼": "\\",
    "〜": "~",
    "｜": "|",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "（": "(",
    "）": ")",
    "〔": "[",
    "〕": "]",
    "［": "[",
    "］": "]",
    "｛": "{",
    "｝": "}",
    "〈": "<",
    "〉": ">",
    "＋": "+",
    "−": "-",
    "＝": "=",
    "＜": "<",
    "＞": ">",
    "′": "'",
    "″": '"',
    "¥": "\\",
    "＄": "$",
    "％": "%",
    "＃": "#",
    "＆": "&",
    "＊": "*",
    "＠": "@",
    "０": "0",
    "１": "1",
    "２": "2",
    "３": "3",
    "４": "4",
    "５": "5",
    "６": "6",
    "７": "7",
    "８": "8",
    "９": "9",
    "Ａ": "A",
    "Ｂ": "B",
    "Ｃ": "C",
    "Ｄ": "D",
    "Ｅ": "E",
    "Ｆ": "F",
    "Ｇ": "G",
    "Ｈ": "H",
    "Ｉ": "I",
    "Ｊ": "J",
    "Ｋ": "K",
    "Ｌ": "L",
    "Ｍ": "M",
    "Ｎ": "N",
    "Ｏ": "O",
    "Ｐ": "P",
    "Ｑ": "Q",
    "Ｒ": "R",
    "Ｓ": "S",
    "Ｔ": "T",
    "Ｕ": "U",
    "Ｖ": "V",
    "Ｗ": "W",
    "Ｘ": "X",
    "Ｙ": "Y",
    "Ｚ": "Z",
    "ａ": "a",
    "ｂ": "b",
    "ｃ": "c",
    "ｄ": "d",
    "ｅ": "e",
    "ｆ": "f",
    "ｇ": "g",
    "ｈ": "h",
    "ｉ": "i",
    "ｊ": "j",
    "ｋ": "k",
    "ｌ": "l",
    "ｍ": "m",
    "ｎ": "n",
    "ｏ": "o",
    "ｐ": "p",
    "ｑ": "q",
    "ｒ": "r",
    "ｓ": "s",
    "ｔ": "t",
    "ｕ": "u",
    "ｖ": "v",
    "ｗ": "w",
    "ｘ": "x",
    "ｙ": "y",
    "ｚ": "z",
}


class Normalizer:
    @staticmethod
    def space(line: str):
        return SPACE_NORM.sub(" ", line)

    @staticmethod
    def nfkc(line: str):
        return unicodedata.normalize("NFKC", line)

    @staticmethod
    def z2h(line: str):
        return line.translate(Z2H_TABLE)

    @staticmethod
    def lower(line: str):
        return line.lower()

    @staticmethod
    def upper(line: str):
        return line.upper()


# fmt: off
@cli.subcommand("normalizer")
@cli.option("--type", "-t", "type", multiple=True, metavar="TYPE", default=["space"],
            choice=["space", "nfkc", "z2h", "lower", "upper"])
# fmt: on
def normalizer(type):
    """Text normalizer

    Text is read from standard input.

    If `--type' is given multiple times, the text will be normalized by
    pipeline.
    \f

    Args:
        type: (List[str]): Normalization types.
    """
    normalizer = [getattr(Normalizer, t) for t in type]
    for line in sys.stdin:
        line = line.strip()
        for norm in normalizer:
            line = norm(line)
        print(line)


if __name__ == "__main__":
    normalize()

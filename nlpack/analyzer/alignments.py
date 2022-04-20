#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unicodedata
from typing import List

import numpy as np
from nlpack import cli

HALFWIDTH_CHARS = {"▁"}


def str_width(string: str):
    return sum(
        2
        if unicodedata.east_asian_width(char) in "FWA" and char not in HALFWIDTH_CHARS
        else 1
        for char in string
    )


def make_hard_matrix(matrix: np.ndarray):
    row_sz, col_sz = matrix.shape
    return [
        "".join("██━" if matrix[i, j] == 1 else "╋━━" for j in range(col_sz))
        for i in range(row_sz)
    ]


def format_matrix(
    matrix: np.ndarray,
    row_labels: List[str],
    column_labels: List[str],
) -> str:
    out_str = ""

    # Get the begin point of columns.
    start_col = max(str_width(label) for label in row_labels) + 1

    # Pad each column label.
    col_len = max(map(len, column_labels))
    padded_column_labels = [
        " " * (col_len - len(label)) + label for label in column_labels
    ]

    # Show the column lables.
    for column_labels_row in zip(*padded_column_labels):
        out_str += " " * start_col
        for char in column_labels_row:
            out_str += f"[green]{char}[/]"
            out_str += " " * (3 - str_width(char))
        out_str += "\n"

    # Pad each row label.
    padded_row_labels = [
        " " * (start_col - str_width(label) - 1) + label for label in row_labels
    ]

    # Show the each row
    matrix_lines = make_hard_matrix(matrix)
    rows_str = "\n".join(
        f"[cyan]{label}[/] {row}" for label, row in zip(padded_row_labels, matrix_lines)
    )
    out_str += rows_str
    return out_str


def show_aligns_one(
    sent_id: int, src_line: str, tgt_line: str, align_line: str, transpose: bool = False
):
    src_line = src_line.strip()
    tgt_line = tgt_line.strip()
    src_tokens = src_line.split()
    tgt_tokens = tgt_line.split()
    aligns = align_line.strip().split()
    align_matrix = np.zeros((len(tgt_tokens), len(src_tokens)), dtype=np.int64)
    for a_i in aligns:
        s, t = a_i.split("-")
        align_matrix[int(t), int(s)] += 1

    matrix_str = (
        format_matrix(align_matrix.T, src_tokens, tgt_tokens)
        if transpose
        else format_matrix(align_matrix, tgt_tokens, src_tokens)
    )

    src_str = ("[cyan]" if transpose else "[green]") + src_line + "[/]"
    tgt_str = ("[green]" if transpose else "[cyan]") + tgt_line + "[/]"

    table = cli.Table(
        title=f"Sentence-{sent_id}",
        title_justify="left",
        show_header=False,
        box=cli.HORIZONTALS,
    )
    table.add_column(justify="right")
    table.add_column(justify="left")
    table.add_row("src", src_str)
    table.add_row("tgt", tgt_str)
    table.add_row("align", "\n" + matrix_str)

    cli.print_no_crop(table)


# fmt: off
@cli.subcommand("show-aligns")
@cli.argument("src_path", metavar="SRC")
@cli.argument("tgt_path", metavar="TGT")
@cli.argument("align_path", metavar="ALIGN")
@cli.option("--transpose", "-t", is_flag=True,
            help="Transpose the alignment matrix.")
# fmt: on
def show_aligns(src_path, tgt_path, align_path, transpose):
    """Show the alignment matrices."""

    with open(src_path) as src_file:
        src_lines = src_file.readlines()
    with open(tgt_path) as tgt_file:
        tgt_lines = tgt_file.readlines()
    with open(align_path) as align_file:
        align_lines = align_file.readlines()

    i = 0
    while i < len(align_lines):
        show_aligns_one(
            i, src_lines[i], tgt_lines[i], align_lines[i], transpose=transpose
        )
        i += 1


if __name__ == "__main__":
    show_aligns()

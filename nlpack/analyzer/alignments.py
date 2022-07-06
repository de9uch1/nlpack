#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

import numpy as np
import wcwidth

from nlpack import cli


def str_width(string: str) -> int:
    return wcwidth.wcswidth(string)


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
    row_widths = [str_width(label) for label in row_labels]
    start_col = max(row_widths) + 1

    # Pad each column label.
    col_len = max(map(len, column_labels))
    padded_column_labels = [
        " " * (col_len - len(label)) + label for label in column_labels
    ]

    # Show the column lables.
    for column_labels_row in zip(*padded_column_labels):
        out_str += " " * start_col
        for char in column_labels_row:
            out_str += cli.style(char, fg="green")
            out_str += " " * (3 - str_width(char))
        out_str += "\n"

    # Pad each row label.
    padded_row_labels = [
        " " * (start_col - width - 1) + label for label, width in zip(row_labels, row_widths)
    ]

    # Show the each row
    matrix_lines = make_hard_matrix(matrix)
    rows_str = "\n".join(
        cli.style(label, fg="cyan") + " " + row for label, row in zip(padded_row_labels, matrix_lines)
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

    cli.echo(f"Sentence-{sent_id}:")
    cli.echo(f"S-{sent_id}\t" + cli.style(src_line, fg="cyan" if transpose else "green"))
    cli.echo(f"T-{sent_id}\t" + cli.style(tgt_line, fg="green" if transpose else "cyan"))
    cli.echo(f"A-{sent_id}\t\n{matrix_str}\n")


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

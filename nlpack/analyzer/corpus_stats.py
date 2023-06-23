#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import concurrent.futures
import fileinput
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Counter, List, Union

from nlpack import cli, utils
from nlpack.utils import SentenceBatch


@dataclass
class CorpusStats:
    num_sentences: int = 0
    num_tokens: int = 0
    sqrd_num_tokens: int = 0
    vocab: Counter = field(default_factory=Counter)
    max_len: int = 0
    max_len_ids: List[int] = field(default_factory=list)
    min_len: int = sys.maxsize
    min_len_ids: List[int] = field(default_factory=list)
    histogram: defaultdict = field(default_factory=lambda: defaultdict(int))

    def get_stats(
        self, sent_id: int, line: Union[str, List[str]], histogram_width: int = 50
    ):
        if isinstance(line, str):
            line = line.split()

        self.num_sentences += 1
        self.vocab.update(line)

        seq_len = len(line)
        self.num_tokens += seq_len
        self.histogram[seq_len // histogram_width] += 1
        self.sqrd_num_tokens += seq_len**2

        if seq_len > self.max_len:
            self.max_len_ids = [sent_id]
            self.max_len = seq_len
        elif seq_len == self.max_len:
            self.max_len_ids.append(sent_id)

        if seq_len < self.min_len:
            self.min_len_ids = [sent_id]
            self.min_len = seq_len
        elif seq_len == self.min_len:
            self.min_len_ids.append(sent_id)

    @classmethod
    def get_stats_batch(cls, batch: SentenceBatch, histogram_width: int):
        self = cls()
        for sent_id, line in zip(batch.ids, batch.lines):
            self.get_stats(sent_id, line, histogram_width)
        return self

    def merge(self, stats):
        self.num_sentences += stats.num_sentences
        self.vocab += stats.vocab
        self.num_tokens += stats.num_tokens
        self.sqrd_num_tokens += stats.sqrd_num_tokens

        for w, v in stats.histogram.items():
            self.histogram[w] += v

        if stats.max_len > self.max_len:
            self.max_len_ids = stats.max_len_ids
            self.max_len = stats.max_len
        elif stats.max_len == self.max_len:
            self.max_len_ids.extend(stats.max_len_ids)

        if stats.min_len < self.min_len:
            self.min_len_ids = stats.min_len_ids
            self.min_len = stats.min_len
        elif stats.min_len == self.min_len:
            self.min_len_ids.extend(stats.min_len_ids)


# fmt: off
@cli.subcommand("corpus-stats")
@cli.argument("input", type=str, default="-", metavar="FILE")
@cli.option("--histogram-width", "-w", type=int, default=10, metavar="N",
            help="Histogram width.")
@cli.option("--buffer-size", "-b", type=int, default=1000000, metavar="N",
            help="Buffer size.")
@cli.option("--quiet", "-q", is_flag=True,
            help="No verbose.")
# fmt: on
def corpus_stats(input: str, histogram_width: int, buffer_size: int, quiet: bool):
    """Show the corpus statistics.

    If FILE is not given, read from standard input.
    """

    results = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        with fileinput.input(files=[input]) as f:
            for batch in utils.buffer_lines(f, buffer_size=buffer_size, strip=True):
                results.append(
                    executor.submit(CorpusStats.get_stats_batch, batch, histogram_width)
                )

    stats = CorpusStats()
    for res in results:
        stats.merge(res.result())

    assert stats.num_sentences > 0, "No input."

    num_tokens_mean = stats.num_tokens / stats.num_sentences
    num_tokens_var = (
        stats.sqrd_num_tokens / stats.num_sentences
    ) - num_tokens_mean**2
    num_tokens_sd = num_tokens_var**0.5

    stats_table_title = "Statistics of {}".format(
        os.path.basename(input) if input != "-" else "(standard input)"
    )
    stats_table = cli.Table(
        title=stats_table_title,
        box=cli.HORIZONTALS,
        show_header=False,
        title_style="bold bright_green",
        title_justify="left",
    )
    stats_table.add_column(style="cyan", justify="left")
    stats_table.add_column(justify="right")
    stats_table.add_column(justify="left")

    stats_table.add_row("# of sentences", f"{stats.num_sentences}")
    stats_table.add_row("# of tokens", f"{stats.num_tokens}")
    stats_table.add_row("# of tokens (mean)", f"{num_tokens_mean:.2f}")
    stats_table.add_row("# of tokens (SD)", f"{num_tokens_sd:.2f}")
    stats_table.add_row("# of vocabulary", f"{len(stats.vocab)}")
    if quiet:
        stats_table.add_row("max length", f"{stats.max_len}")
        stats_table.add_row("min length", f"{stats.min_len}")
    else:
        stats_table.add_row(
            "max length", f"{stats.max_len}", f"line: {stats.max_len_ids}"
        )
        stats_table.add_row(
            "min length", f"{stats.min_len}", f"line: {stats.min_len_ids}"
        )
    cli.rprint(stats_table)
    cli.rprint()

    histogram_table = cli.Table(
        title=f"Histogram of sentence lengths \[width: {histogram_width}]",
        box=cli.HORIZONTALS,
        show_header=False,
        title_style="bold bright_green",
        title_justify="left",
    )
    histogram_table.add_column(style="cyan", justify="right")
    histogram_table.add_column(header="range", style="cyan", justify="center")
    histogram_table.add_column(style="cyan", justify="right")
    histogram_table.add_column(justify="left")
    histogram_table.add_column(justify="right")
    histogram_table.add_column(justify="right")

    num_sentences = stats.num_sentences
    histogram = stats.histogram
    for i in range(max(histogram) + 1):
        start = i * histogram_width
        end = (i + 1) * histogram_width - 1 if i < max(histogram) else stats.max_len
        count = histogram[i]
        percentage = (count / num_sentences) * 100
        bar = cli.Bar(size=100, begin=0, end=percentage, width=30)
        histogram_table.add_row(
            f"{start}",
            "\u2013",
            f"{end}",
            bar,
            f"{count}",
            f"[green][ {percentage:>6.2f} % ]",
        )
    cli.rprint(histogram_table)


if __name__ == "__main__":
    corpus_stats()

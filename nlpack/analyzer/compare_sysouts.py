#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import concurrent.futures
import os
import re
from typing import List, Optional

import numpy as np
from rich.console import Console
from sacrebleu.dataset import DATASETS
from sacrebleu.metrics import BLEU, CHRF, TER
from sacrebleu.utils import get_reference_files, smart_open

from nlpack import cli


class SentenceWiseScorer:

    TAG_PATTERN = re.compile(r"^<(.+)>$")
    MINIMIZE_METRICS = {"ter"}

    def __init__(
        self,
        metric: str,
        test_set: str,
        lowercase: bool = False,
        tokenize: str = "13a",
        langpair: Optional[str] = None,
        source_file: Optional[str] = None,
    ):
        self.metric = metric
        self.ref = self.read_reference(test_set)
        self.langpair = langpair
        self.scorer = self.build_scorer(metric, lowercase=lowercase, tokenize=tokenize)
        self.minimize_metric = metric in self.MINIMIZE_METRICS

        self.scores = []
        self.sysouts = []

        self.source = []
        if source_file is not None:
            with open(source_file) as f:
                for line in f:
                    self.source.append(line.strip())

    def build_scorer(
        self,
        metric: str,
        lowercase: bool = False,
        tokenize: str = "v13a",
    ):
        if metric == "bleu":
            return BLEU(
                lowercase=lowercase,
                tokenize=tokenize,
                effective_order=True,
            )
        elif metric == "ter":
            return TER(
                case_sensitive=not lowercase,
            )
        elif metric == "chrf":
            return CHRF(
                lowercase=lowercase,
            )
        else:
            raise NotImplementedError

    def read_reference(self, test_set: str) -> List[str]:
        ref = []
        if os.path.exists(test_set):
            with open(test_set) as f:
                for line in f:
                    ref.append([line.strip()])
        elif DATASETS.get(test_set, None) is not None:
            assert self.langpair is not None
            ref_file = get_reference_files(test_set, self.langpair)
            for line in smart_open(ref_file):
                ref.append([line.strip()])
        return ref

    def score_sentences(self, lines: List[str]):
        with concurrent.futures.ProcessPoolExecutor() as executor:
            return list(executor.map(self.scorer.sentence_score, lines, self.ref))

    def add_hypo(self, hypos: List[str]):
        self.scores.append(self.score_sentences(hypos))
        self.sysouts.append(hypos)

    def compare_systems(
        self,
        sort_score: Optional[int] = None,
        sort_diff: Optional[int] = None,
        format_style: str = "plain",
    ):
        if sort_score is not None:
            sort_indices = np.argsort(
                [s.score for s in self.scores[sort_score]], kind="mergesort"
            )
            if not self.minimize_metric:
                sort_indices = sort_indices[::-1]
        elif sort_diff is not None:
            sort_indices = np.argsort(
                np.array([s.score for s in self.scores[sort_diff]])
                - np.array([s.score for s in self.scores[0]]),
                kind="mergesort",
            )
            if not self.minimize_metric:
                sort_indices = sort_indices[::-1]
        else:
            sort_indices = np.arange(len(self.ref))

        if format_style == "plain":
            self.format_plain(sort_indices)
        elif format_style == "pretty":
            self.format_pretty(sort_indices)
        else:
            raise NotImplementedError

    def format_pretty(self, sort_indices: np.ndarray):
        greaters = [{} for _ in self.sysouts]
        lowers = [{} for _ in self.sysouts]
        equals = [{} for _ in self.sysouts]

        console = Console()
        with console.pager(styles=True):
            for i in sort_indices:
                table = cli.Table(
                    title=f"Sentence-{i}",
                    title_justify="left",
                    show_header=False,
                    box=cli.HORIZONTALS,
                )
                table.add_column(justify="right", style="cyan")
                table.add_column(justify="right")
                table.add_column(justify="left")

                if len(self.source) != 0:
                    table.add_row("Src", None, self.source[i])
                ref_i = self.ref[i][0]
                table.add_row("Ref", None, ref_i)
                sys0_score = 0.0
                for sysno, hypo in enumerate(self.sysouts):
                    if sysno == 0:
                        sys0_score = self.scores[sysno][i].score
                    score = self.scores[sysno][i].score
                    if (self.minimize_metric and score < sys0_score) or (
                        not self.minimize_metric and score > sys0_score
                    ):
                        greaters[sysno][i] = score
                    elif (self.minimize_metric and score > sys0_score) or (
                        not self.minimize_metric and score < sys0_score
                    ):
                        lowers[sysno][i] = score
                    else:
                        equals[sysno][i] = score

                    gain = score - sys0_score
                    if sysno == 0:
                        score_color = "[default]"
                    elif (self.minimize_metric and gain <= 0) or (
                        not self.minimize_metric and gain >= 0
                    ):
                        score_color = "[green]"
                    else:
                        score_color = "[red]"
                    table.add_row(
                        f"Sys{sysno}",
                        f"{score_color}{score:>6.2f} ({gain:>+6.2f})",
                        f"{hypo[i].strip()}",
                    )
                console.print(table)
                console.print("")

            num_sents = len(self.ref)
            table = cli.Table(
                title=f"Statistics:",
                title_justify="left",
                title_style="bold purple",
                show_header=False,
                box=cli.ROUNDED,
            )
            table.add_column(justify="left", style="cyan")
            table.add_column(justify="right")
            table.add_column(justify="right")
            table.add_column(justify="right")

            for sysno, (gt, lt, eq) in enumerate(zip(greaters, lowers, equals)):
                table.add_row(
                    f"System{sysno}",
                    "↑{:6.2f}: {:5d}/{:5d} ({:6.2f} %)".format(
                        sum(gt.values()) / len(gt) if len(gt) > 0 else 0.0,
                        len(gt),
                        num_sents,
                        len(gt) / num_sents * 100,
                    ),
                    "↓{:6.2f}: {:5d}/{:5d} ({:6.2f} %)".format(
                        sum(lt.values()) / len(lt) if len(lt) > 0 else 0.0,
                        len(lt),
                        num_sents,
                        len(lt) / num_sents * 100,
                    ),
                    "→{:6.2f}: {:5d}/{:5d} ({:6.2f} %)".format(
                        sum(eq.values()) / len(eq) if len(eq) > 0 else 0.0,
                        len(eq),
                        num_sents,
                        len(eq) / num_sents * 100,
                    ),
                )
            console.print(table)

    def format_plain(self, sort_indices: np.ndarray):
        greaters = [{} for _ in self.sysouts]
        lowers = [{} for _ in self.sysouts]
        equals = [{} for _ in self.sysouts]

        for i in sort_indices:
            if len(self.source) != 0:
                print("Source-{}\t{}".format(i, self.source[i]))
            ref_i = self.ref[i][0]
            print("Reference-{}\t{}".format(i, ref_i))
            sys0_score = 0.0
            for sysno, hypo in enumerate(self.sysouts):
                if sysno == 0:
                    sys0_score = self.scores[sysno][i].score
                score = self.scores[sysno][i].score
                if (self.minimize_metric and score < sys0_score) or (
                    not self.minimize_metric and score > sys0_score
                ):
                    greaters[sysno][i] = score
                elif (self.minimize_metric and score > sys0_score) or (
                    not self.minimize_metric and score < sys0_score
                ):
                    lowers[sysno][i] = score
                else:
                    equals[sysno][i] = score
                print(
                    "System{}-{}\t{:.2f} ({:+.2f})\t{}".format(
                        sysno,
                        i,
                        score,
                        score - sys0_score,
                        hypo[i].strip(),
                    )
                )
            print("")
        num_sents = len(self.ref)
        print("| Sentences: {}".format(num_sents))
        for sysno, (gt, lt, eq) in enumerate(zip(greaters, lowers, equals)):
            print(
                "| System{}:\t↑{:.2f}: {}/{} ({:.2f} %) ↓{:.2f}: {}/{} ({:.2f} %) →{:.2f}: {}/{} ({:.2f} %)".format(
                    sysno,
                    sum(gt.values()) / len(gt) if len(gt) > 0 else 0.0,
                    len(gt),
                    num_sents,
                    len(gt) / num_sents * 100,
                    sum(lt.values()) / len(lt) if len(lt) > 0 else 0.0,
                    len(lt),
                    num_sents,
                    len(lt) / num_sents * 100,
                    sum(eq.values()) / len(eq) if len(eq) > 0 else 0.0,
                    len(eq),
                    num_sents,
                    len(eq) / num_sents * 100,
                )
            )


# fmt: off
@cli.subcommand("compare-sysouts")
@cli.option("--metric", choice=["bleu", "ter", "chrf"], metavar="METRIC", default="bleu",
            help="Metrics")
@cli.option("--test-set", "-t", type=str, metavar="TEST_SET", required=True,
            help="Test set name or path")
@cli.option("--language-pair", "-l", type=str, metavar="LANGPAIR",
            help="Language pair")
@cli.option("--lowercase", is_flag=True,
            help="Case-insensitive")
@cli.option("--tokenize", "-tok", type=str, metavar="TOKENIZE", default="13a",
            help="Tokenizer name")
@cli.option("--sysout", "--hypo", "-o", type=str, metavar="FILE", multiple=True,
            help="System outputs (can be specify multiple times.)")
@cli.option("--source", "-s", type=str, metavar="FILE", default=None,
            help="Source file")
@cli.option("--sort-score", type=int, metavar="SYSNO", default=None,
            help="Sort by the SYSNO-th system scores.")
@cli.option("--sort-gain", type=int, metavar="SYSNO", default=None,
            help="Sort by the difference between the baseline system and SYSNO-th system scores.")
@cli.option("--format-style", "-f", choice=["pretty", "plain"], metavar="FORMAT", default="pretty",
            help="Format style.")
# fmt: on
def compare_sysouts(
    metric: str,
    test_set: str,
    language_pair: str,
    lowercase: bool,
    tokenize: str,
    sysout: List[str],
    source: str,
    sort_score: Optional[int],
    sort_gain: Optional[int],
    format_style: str,
):
    """Compare multiple system outputs with the reference.

    It can be also showed outputs sorted by the N-th system score or score gain.
    """
    scorer = SentenceWiseScorer(
        metric,
        test_set,
        lowercase=lowercase,
        tokenize=tokenize,
        langpair=language_pair,
        source_file=source,
    )
    for hypo_file in sysout:
        with open(hypo_file, mode="r") as f:
            scorer.add_hypo(f.readlines())
    scorer.compare_systems(
        sort_score=sort_score,
        sort_diff=sort_gain,
        format_style=format_style,
    )


if __name__ == "__main__":
    compare_sysouts()

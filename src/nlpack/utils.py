# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import json
from dataclasses import dataclass
from typing import Generator, Iterable, Optional


@dataclass
class SentenceBatch:
    ids: list[int]
    lines: list[str]

    def __len__(self):
        return len(self.ids)


def buffer_lines(
    lines: Iterable,
    buffer_size: int = 10000,
    strip: bool = True,
    jsonl_key: Optional[str] = None,
) -> Generator[SentenceBatch, None, None]:
    buf: list[str] = []
    ids: list[int] = []

    json_decoder = None
    if jsonl_key is not None:
        json_decoder = json.JSONDecoder()

    for idx, line in enumerate(lines, start=1):
        if strip:
            line = line.strip()
        if json_decoder is not None:
            line = json_decoder.decode(line)[jsonl_key]

        buf.append(line)
        ids.append(idx)
        if len(buf) >= buffer_size:
            yield SentenceBatch(ids, buf)
            buf, ids = [], []

    if len(buf) > 0:
        yield SentenceBatch(ids, buf)

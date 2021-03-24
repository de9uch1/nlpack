# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from dataclasses import dataclass
from typing import Iterable, List, Optional, Union


@dataclass
class SentenceBatch:
    ids: List[int]
    lines: List[Union[str, List[str]]]

    def __len__(self):
        return len(self.ids)


def buffer_lines(
    lines: Iterable,
    buffer_size: int = 10000,
    strip: bool = True,
    split: bool = False,
    delim: Optional[str] = None,
) -> List[SentenceBatch]:
    buf, ids = [], []
    for idx, line in enumerate(lines, start=1):
        if strip:
            line = line.strip()
        if split:
            line = line.split(delim)
        buf.append(line)
        ids.append(idx)
        if len(buf) >= buffer_size:
            yield SentenceBatch(ids, buf)
            buf, ids = [], []

    if len(buf) > 0:
        yield SentenceBatch(ids, buf)

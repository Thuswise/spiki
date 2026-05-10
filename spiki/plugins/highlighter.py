#!/usr/bin/env python
#   encoding: utf-8

# Copyright (C) 2026 D E Haynes
# This file is part of spiki.

# Spiki is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# Spiki is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with spiki.
# If not, see <https://www.gnu.org/licenses/>.


import itertools
from pathlib import Path
import random

from spiki.plugin import Change
from spiki.plugin import Plugin


class Highlighter(Plugin):

    @classmethod
    def find_code(cls, node: dict):
        for k, v in node.items():
            if isinstance(v, list):
                for i in (i for i in v if isinstance(i, dict)):
                    yield from list(cls.find_code(i))
            elif isinstance(v, dict):
                yield from cls.find_code(v)

            if k == "code":
                yield node

    def run_extend(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> None | Change:
        targets = list(itertools.chain(self.find_code(node)))
        self.logger.info(
            f"{targets=}",
            extra=dict(path=path.name, phase=self.phase),
        )
        for n, target in enumerate(targets):
            try:
                define = target.pop("define")
            except KeyError:
                continue

            blocks = section.get("blocks", [])
            try:
                template = blocks.pop(0)
                data_path = self.visitor.location_of(node).parent.joinpath(define["file"]).resolve()
                for index, row in enumerate(self.sources.get(data_path, [])):
                    punc = random.choice("?!.")
                    text = template.format(define=dict(define, index=index, punc=punc, **row))
                    blocks.append(text)
                self.logger.info(
                    f"Substituted {index + 1} rows of data from {data_path.name}",
                    extra=dict(path=path.name, phase=self.phase),
                )
            except (IndexError, KeyError) as error:
                self.logger.warning(
                    f"{type(error).__name__}: {error} (section {n}, row {index})",
                    extra=dict(path=path.name, phase=self.phase)
                )
                continue

        return Change(self, path=path, node=node, doc=doc)

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


import csv
import logging
from pathlib import Path
import random

from spiki.plugin import Change
from spiki.plugin import Plugin
from spiki.renderer import Renderer


class Templater(Plugin):

    def __init__(self, visitor):
        super().__init__(visitor)
        self.sources = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rv = super().__exit__(exc_type, exc_val, exc_tb)
        return rv

    def run_ingest(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Change:
        if path.suffix == ".csv":
            with path.open(newline="") as data_file:
                reader = csv.DictReader(data_file)
                self.sources[path] = list(reader)

        return Change(self, path=path, node=node, doc=doc)

    def run_extend(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Change:
        try:
            sections = node["doc"]["html"]["body"]["main"].get("section", [])
        except KeyError:
            sections = []

        for n, section in enumerate(sections):
            try:
                define = section.pop("define")
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
            except (IndexError, KeyError) as error:
                self.logger.warning(
                    f"{type(error).__name__}: {error} (section {n}, row {index})",
                    extra=dict(path=path.name, phase=self.phase)
                )
                continue

            self.logger.info(f"{path=}")
        # TODO: Pop define key

        return Change(self, path=path, node=node, doc=doc)

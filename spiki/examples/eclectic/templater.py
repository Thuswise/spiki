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
from pathlib import Path
import random

from spiki.plugin import Change
from spiki.plugin import Plugin


class Templater(Plugin):

    def __init__(self, visitor):
        """
        Plugins rely on behaviour provided by the base class.
        If you want your own initializer you'll also need to invoke that of the parent.

        Plugins are context managers so the same applies to the __enter__ and __exit__ methods.

        """
        super().__init__(visitor)
        self.sources = {}

    def run_ingest(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> None | Change:
        """
        Plugin methods are invoked in sequence. See `spiki.plugin.Phase` for the significance of each phase.
        This example looks for tabular data in local CSV files.

        """
        if path.suffix == ".csv":
            with path.open(encoding="utf8", newline="") as data_file:
                reader = csv.DictReader(data_file)
                self.sources[path] = list(reader)

    def run_extend(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> None | Change:
        """
        This method looks for sections with a `define` attribute. It uses the nearby SpeechMark block as
        a template for dialogue and substitutes row by row from the indicated file.

        We return a `spiki.plugin.Change` object because we have modified the existing content.

        """
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

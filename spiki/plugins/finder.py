#!/usr/bin/env python
#   encoding: utf-8

# Copyright (C) 2025 D E Haynes
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

from collections.abc import Generator
import logging
import mimetypes
from pathlib import Path

from spiki.plugin import Change
from spiki.plugin import Plugin


class Finder(Plugin):

    def __init__(self, visitor):
        super().__init__(visitor)
        self.logger = logging.getLogger("finder")

    def __enter__(self):
        mimetypes.add_type("application/toml", ".toml", strict=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rv = super().__exit__(exc_type, exc_val, exc_tb)
        return rv

    @staticmethod
    def get_type(path: Path):
        try:
            t = mimetypes.guess_file_type(path, strict=False)  # Python 3.13
        except AttributeError:
            t = mimetypes.guess_type(path, strict=False)
        try:
            return t[0] or ""
        except IndexError:
            return ""

    def gen_survey(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Generator[Change]:
        for parent, dirnames, filenames in path.resolve().walk():
            self.logger.info(f"Visiting {parent}...", extra=dict(phase=self.phase))
            for name in sorted(filenames):
                file_type = self.get_type(name)
                p = parent.joinpath(name)
                self.logger.info(f"Found {file_type:<16} file: {name}", extra=dict(path=p, phase=self.phase))
                if file_type:
                    yield Change(self, path=p, type=file_type)

    def run_ingest(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Change:
        file_type = self.get_type(path.name)
        if "image" in file_type:
            return Change(self, path=path, type=file_type)
        return Change(self, path=path, text=path.read_text(), type=file_type)

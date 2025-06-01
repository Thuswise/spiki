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

import logging
from pathlib import Path

from spiki.plugin import Plugin
from spiki.plugin import Event


class Finder(Plugin):

    def __init__(self, visitor):
        super().__init__(visitor)
        self.logger = logging.getLogger("finder")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rv = super().__exit__(exc_type, exc_val, exc_tb)
        return rv

    def do_survey(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Event:
        for parent, dirnames, filenames in path.resolve().walk():
            for name in sorted(filenames):
                p = parent.joinpath(name)
                return Event(self, path=p, text=p.read_text())


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

import argparse
import importlib.resources
import sys
import tempfile
import zipfile

from spiki.plugin import Change
from spiki.plugin import Plugin


class Bootstrapper(Plugin):

    def end_export(self, **kwargs) -> Change:
        output = self.visitor.options["output"]
        print(f"{output=}")
        return Change(self)

"""
frozen = getattr(sys, "frozen", None)
root = importlib.resources.files()

for path in root.iterdir():
    print(path, type(path))
"""

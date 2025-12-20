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
import pathlib
import sys
import zipapp
import tempfile
import zipfile

from spiki.plugin import Change
from spiki.plugin import Plugin


class Bootstrapper(Plugin):

    def end_extend(self, **kwargs) -> Change:
        path = self.visitor.root.joinpath("__main__.py")
        node = dict(metadata=dict(slug=path.name))
        self.logger.info(f"Generating a {path.name}", extra=dict(path=path, phase=self.phase))
        return Change(self, path=path, text="#", node=node, phase=self.phase)

    def end_export(self, **kwargs) -> Change:
        path = self.visitor.root.joinpath("__main__.py")
        change = self.visitor.state[path]
        source = change.result.parent

        output = self.visitor.options["output"]
        target = output.with_suffix(".pyz")
        self.logger.info(f"Creating {target}", extra=dict(path=path, phase=self.phase))
        zipapp.create_archive(source, target=target)


"""
frozen = getattr(sys, "frozen", None)
root = importlib.resources.files()

for path in root.iterdir():
    print(path, type(path))
"""

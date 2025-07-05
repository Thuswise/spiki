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
import shutil
import tempfile

from spiki.plugin import Change
from spiki.plugin import Plugin
from spiki.renderer import Renderer


class Writer(Plugin):

    def __init__(self, visitor):
        super().__init__(visitor)
        self.logger = logging.getLogger("writer")
        self.space = None

    def __enter__(self):
        self.space = Path(tempfile.mkdtemp()).resolve()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rv = super().__exit__(exc_type, exc_val, exc_tb)
        shutil.rmtree(self.space, ignore_errors=True)
        return rv

    def run_render(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Change:
        doc = Renderer(node).serialize()
        return Change(self, path=path, node=node, doc=doc)

    def run_export(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Change:
        route = path.relative_to(self.visitor.root).parent
        parent = self.space.joinpath(route).resolve()
        slug = node["metadata"]["slug"]

        if path.suffix == ".toml":
            dest = parent.joinpath(slug).with_suffix(".html")
            text = doc
        else:
            dest = parent.joinpath(slug).with_suffix(path.suffix)
            text = self.visitor.state[path].text

        self.logger.info(f"Exporting to {dest.relative_to(self.space)}", extra=dict(path=path, phase=self.phase))
        try:
            dest.write_text(text)
        except TypeError:
            dest.write_bytes(text)
        except Exception:
            self.logger.warning(
                f"Unable to write document for {path.relative_to(self.visitor.root)}",
                extra=dict(path=path, phase=self.phase)
            )
        else:
            return Change(self, path=path, node=node, doc=doc, result=dest)

    def end_export(self, **kwargs) -> Change:
        output = self.visitor.options["output"]
        shutil.copytree(self.space, output, dirs_exist_ok=True)
        return Change(self)

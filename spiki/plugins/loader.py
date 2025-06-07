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

import datetime
import logging
from pathlib import Path
import tomllib

from spiki.plugin import Change
from spiki.plugin import Plugin


class Loader(Plugin):

    def __init__(self, visitor):
        super().__init__(visitor)
        self.logger = logging.getLogger("loader")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rv = super().__exit__(exc_type, exc_val, exc_tb)
        return rv

    def do_ingest(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Change:
        text = self.visitor.state[path].text
        node = tomllib.loads(text)
        return Change(self, path=path, node=node)

    def do_enrich(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Change:
        node.setdefault("registry", {})["path"] = path
        node["registry"]["root"] = self.root
        node["registry"]["node"] = path.parent.relative_to(self.root).parts
        node["registry"]["time"] = datetime.datetime.now(tz=datetime.timezone.utc)

        node.setdefault("metadata", {})["slug"] = (
            node.get("metadata", {}).get("slug") or
            self.slugify("_".join(path.relative_to(self.root).with_suffix("").parts))
        )
        node["metadata"]["title"] = node["metadata"].get("title", path.name)
        return Change(self, path=path, node=node)

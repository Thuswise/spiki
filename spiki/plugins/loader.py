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
import functools
import logging
from pathlib import Path
import tomllib

from spiki.plugin import Change
from spiki.plugin import Plugin


class Loader(Plugin):

    @staticmethod
    def slices(parts: tuple):
        return [tuple()] if not parts else [parts[:n] for n in range(len(parts) + 1)]

    @staticmethod
    def merge(*args: tuple[dict]) -> dict:
        bases = [dict(doc=i.get("base", {})) for i in args if "base" in i]
        end = (args or [{}])[-1]
        return functools.reduce(Loader.combine, bases + [end])

    @staticmethod
    def combine(lhs: dict, rhs: dict) -> dict:
        "Use lhs as a base to update rhs"
        for k, v in lhs.items():
            try:
                node = rhs[k]
                if isinstance(node, dict):
                    rv = Loader.combine(v, node)
                    lhs_keys = list(v)
                    rhs_keys = [i for i in node if i not in set(lhs_keys)]
                    rhs[k] = {k: rv[k] for k in lhs_keys + rhs_keys}
                elif isinstance(node, list):
                    rhs[k] = v + node
            except KeyError:
                rhs[k] = v
        return rhs

    def __init__(self, visitor):
        super().__init__(visitor)
        self.logger = logging.getLogger("loader")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rv = super().__exit__(exc_type, exc_val, exc_tb)
        return rv

    def run_ingest(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Change:
        text = self.visitor.state[path].text
        try:
            node = tomllib.loads(text)
        except (AttributeError, TypeError, tomllib.TOMLDecodeError):
            self.logger.warning(
                f"Unable to read data from {path.relative_to(self.visitor.root)}",
                extra=dict(phase=self.phase)
            )
        else:
            return Change(self, path=path, node=node)

    def run_enrich(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Change:
        node.setdefault("registry", {})["path"] = path
        node["registry"]["root"] = self.visitor.root
        node["registry"]["node"] = path.parent.relative_to(self.visitor.root).parts
        node["registry"]["time"] = datetime.datetime.now(tz=datetime.timezone.utc)

        node.setdefault("metadata", {})["slug"] = (
            node.get("metadata", {}).get("slug") or
            self.slugify("_".join(path.relative_to(self.visitor.root).with_suffix("").parts))
        )
        node["metadata"]["title"] = node["metadata"].get("title", path.name)
        return Change(self, path=path, node=node)

    def run_extend(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Change:
        self.logger.info(f"extend node {path} from index base how?", extra=dict(phase=self.phase))

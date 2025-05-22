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
from collections import defaultdict
import logging
from pathlib import Path
import tomllib

from spiki.plugin import Phase
from spiki.plugin import Plugin


class Indexer(Plugin):

    def __init__(self, visitor):
        super().__init__(visitor)
        self.indexes = {}

    def __call__(
        self,
        phase: Phase, *,
        path: Path = None,
        node: dict = None,
        doc: str = None,
        **kwargs
    ) -> bool:
        logger = logging.getLogger("indexer")
        if phase == Phase.SURVEY:
            if path.name == self.visitor.index_name:
                logger.info(node["registry"]["path"], extra=dict(phase=phase))
                key = node["registry"]["node"]
                self.indexes[key] = node
                return True
        elif phase == Phase.ENRICH:
            try:
                # root
                root_index = self.indexes[next(iter(sorted(self.indexes)))]
                print(root_index["registry"]["path"])
                # home
                # back
                # here
                # down
                index_path = next(reversed(self.visitor.ancestors(path)))
                index = self.visitor.nodes[index_path]
                node["registry"]["index"] = index
                index["registry"].setdefault("nodes", []).append(node)
                # TODO: nav.header and nav.footer inside nav
                text = f"""
                [doc.html.body.nav]
                config = {{tag_mode = "pair"}}
                [[doc.html.body.nav.header.ul.li]]
                attrib = {{href = "{node['metadata']['slug']}.html"}}
                a = "{node['metadata']['title']}"
                """
                data = tomllib.loads(text)
                rhs = self.visitor.combine(data, index)
                return True
            except (KeyError, StopIteration) as error:
                return False
        elif phase == Phase.REPORT:
            logger.info(f"{list(self.indexes)=}", extra=dict(phase=phase))
            return False
        return False

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

from pathlib import Path
import tempfile
import textwrap
import tomllib
import unittest

from spiki.pathfinder import Pathfinder
from spiki.plugins.indexer import Indexer


class IndexerTests(unittest.TestCase):

    def test_survey(self):
        with tempfile.TemporaryDirectory() as src_name:
            src = Path(src_name).resolve()
            index = src.joinpath("index.toml")
            index.write_text("")
            pathfinder = Pathfinder()
            with Indexer(pathfinder) as indexer:
                index_node = pathfinder.nodes[index] = pathfinder.build_node(index, root=src)
                indexer.do_survey(path=index, node=index_node)
                self.assertTrue(indexer.indexes)
                self.assertEqual(pathfinder.url_of(index_node), "index.html")

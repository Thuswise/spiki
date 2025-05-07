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

import textwrap
import tomllib
import unittest

from spiki.renderer import Renderer


class PathfinderTests(unittest.TestCase):

    def test_merge_base(self):
        index_toml = textwrap.dedent("""
        [base]
        config = {tag_mode = "pair"}

        [[base.html.body.nav.ul.li]]
        attrib = {href = "/"}
        a = "Home"

        """)
        index = tomllib.loads(index_toml)

        node_toml = textwrap.dedent("""
        [[doc.html.body.nav.ul.li]]
        attrib = {href = "/faq.html"}
        a = "FAQ"

        """)
        node = tomllib.loads(node_toml)

        # template = Pathfinder.merge(index, node)
        template = dict(doc=index["base"])
        rv = Renderer().serialize(template)
        self.assertEqual(rv.count("href"), 2)
        print(rv)

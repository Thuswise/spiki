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

from spiki.pathfinder import Pathfinder
from spiki.renderer import Renderer


class PathfinderTests(unittest.TestCase):

    def test_slug(self):
        text = "ABab234$%^&*-_ "
        rv = Pathfinder.slugify(text)
        self.assertEqual("abab234-_-", rv)

    def test_stack(self):
        parts = tuple()
        slices = Pathfinder.slices(parts)
        self.assertEqual(slices, [(),])

        parts = (1, 2, 3, 4)
        slices = Pathfinder.slices(parts)
        self.assertEqual(slices, [(), (1,), (1, 2), (1, 2, 3), (1, 2, 3, 4)])

    def test_merge_null(self):
        rv = Pathfinder().merge()
        self.assertEqual(rv, {})

    def test_combine(self):
        lhs = dict(a=dict(b=1, c=2), b=[dict(d=3, e=4), dict(f=5, g=6)])
        rhs = dict(a=dict(b=10), b=[dict(d=30, e=40)])
        rv = Pathfinder().combine(lhs, rhs)
        self.assertIs(rv, rhs)
        self.assertEqual(rv["a"]["b"], 10)
        self.assertEqual(rv["a"]["c"], 2)
        self.assertEqual(len(rv["b"]), 3)

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

        template = Pathfinder().merge(index, node)
        self.assertEqual(template["doc"]["config"]["tag_mode"], "pair")
        rv = Renderer().serialize(template)
        self.assertEqual(rv.count("href"), 2, rv)

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

import importlib.resources
import pathlib
import tempfile
import textwrap
import tomllib
import unittest

import spiki
from spiki.plugin import Phase
from spiki.renderer import Renderer
from spiki.visitor import Visitor


class VisitorTests(unittest.TestCase):

    def test_slug(self):
        text = "ABab234$%^&*-_ "
        rv = Visitor.slugify(text)
        self.assertEqual("abab234-_-", rv)

    def test_stack(self):
        parts = tuple()
        slices = Visitor.slices(parts)
        self.assertEqual(slices, [(),])

        parts = (1, 2, 3, 4)
        slices = Visitor.slices(parts)
        self.assertEqual(slices, [(), (1,), (1, 2), (1, 2, 3), (1, 2, 3, 4)])

    def test_merge_null(self):
        rv = Visitor().merge()
        self.assertEqual(rv, {})

    def test_merge_bases(self):
        a = f"""
        [base.one.two]
        n = 0
        [base.two.one]
        n = 0
        """
        b = f"""
        [[base.two.two]]
        n = 1
        [base.two.one]
        n = 1
        [base.one.two]
        n = 1
        """
        c = f"""
        [[doc.two.two]]
        n = 2
        [doc.two.one]
        n = 2
        """
        d = f"""
        [[doc.two.two]]
        n = 3
        [doc.two.one]
        n = 3
        """
        # Test base defining defaults for doc
        args = [tomllib.loads(i) for i in (a, b, c)]
        rv = Visitor().merge(*args)
        self.assertEqual(list(rv["doc"]), ["one", "two"])
        self.assertEqual(list(rv["doc"]["two"]), ["one", "two"])
        self.assertEqual(rv["doc"]["two"]["one"]["n"], 2)
        self.assertEqual([i["n"] for i in rv["doc"]["two"]["two"]], [1, 2])

        # Test doc overriding previous
        arg = tomllib.loads(d)
        rv = Visitor().merge(rv, arg)
        self.assertEqual(list(rv["doc"]), ["two"])
        self.assertEqual(list(rv["doc"]["two"]), ["two", "one"])

    def test_combine(self):
        lhs = dict(a=dict(b=1, c=2), b=[dict(d=3, e=4), dict(f=5, g=6)])
        rhs = dict(a=dict(b=10), b=[dict(d=30, e=40)])
        rv = Visitor().combine(lhs, rhs)
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

        template = Visitor().merge(index, node)
        self.assertEqual(template["doc"]["config"]["tag_mode"], "pair")
        rv = Renderer().serialize(template)
        self.assertEqual(rv.count("href"), 2, rv)

    def test_example(self):
        plugin_types = [
            "spiki.plugins.finder:Finder",
            "spiki.plugins.loader:Loader",
            # "spiki.plugins.indexer:Indexer",
            "spiki.plugins.writer:Writer",
        ]
        examples = importlib.resources.files("spiki.examples")
        witness = []
        with (
            tempfile.TemporaryDirectory() as output_name,
            Visitor(*plugin_types) as visitor,
        ):
            visitor.options = dict(
                output=pathlib.Path(output_name).resolve(),
                paths=[examples.joinpath("atom")],
            )

            self.assertFalse(visitor.state)
            for event in visitor.walk(*visitor.options["paths"]):
                witness.append(event)
                if event.phase == Phase.ENRICH:
                    print(f"{event.node=}")
                    destination = visitor.location_of(event.node).relative_to(event.node["registry"]["root"]).parent
                    print(f"{destination=}")

            print(*witness, sep="\n")
            self.assertEqual(len(visitor.state), 1, visitor.state)
            path = list(visitor.state)[0]
            self.assertEqual("a.toml", path.name)
            self.assertEqual(visitor.state[path].node["doc"]["html"]["body"]["blocks"], ["    Hello, World!\n\n    "])

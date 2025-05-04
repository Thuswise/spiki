#!/usr/bin/env python
#   encoding: utf-8

# This is part of the speechmark library.
# Copyright (C) 2025 D E Haynes

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

import textwrap
import tomllib
import unittest

from speechmark.spiki.renderer import Renderer


class RendererTests(unittest.TestCase):

    def test_config_option(self):
        toml = textwrap.dedent("""
        [doc]
        config = {tag_mode = "invalid"}
        """)
        template = tomllib.loads(toml)
        r = Renderer()
        with self.assertWarns(UserWarning) as context:
            rv = r.serialize(template)
        self.assertFalse(rv)
        self.assertIn("invalid", format(context.warning))

    def test_head(self):
        test = "Essential head content"
        goal = textwrap.dedent(f"""
        <!doctype html>
        <html lang="en">
        <head>
        <title>{test}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        </head>
        </html>
        """).strip()

        toml = textwrap.dedent("""
        [doc]
        config = {tag_mode = "open"}

        "!doctype html" = ""

        [doc.html]
        config = {tag_mode = "pair"}
        attrib = {lang = "en"}

        [doc.html.head]
        title = ""

        [[doc.html.head.meta]]
        config = {tag_mode = "open"}
        attrib = {charset = "UTF-8"}

        [[doc.html.head.meta]]
        config = {tag_mode = "void"}
        attrib = {name = "viewport", content = "width=device-width, initial-scale=1.0"}

        [[doc.html.head.meta]]
        config = {tag_mode = "open"}
        attrib = {http-equiv = "X-UA-Compatible", content = "ie=edge"}

        """)

        template = tomllib.loads(toml)
        template["doc"]["html"]["head"]["title"] = test
        rv = Renderer().serialize(template)
        self.assertEqual(rv, goal, template)

    def test_block(self):
        test = "Single speech block"
        toml = textwrap.dedent("""
        [doc]

        [doc.html]
        config = {tag_mode = "pair"}

        [doc.html.head]
        title = ""

        [doc.html.body]
        blocks = [
            '''
            <STAFF.suggesting#3> What would you like sir? We have some very good fish today.
                1. Order the Beef Wellington
                2. Go for the Cottage Pie
                3. Try the Dover Sole

            '''
        ]

        """)
        template = tomllib.loads(toml)
        template["doc"]["html"]["head"]["title"] = test
        rv = Renderer().serialize(template)
        self.assertTrue(rv.startswith("<html>"))
        self.assertTrue(rv.endswith("</html>"))
        self.assertIn("<body>", rv)
        self.assertIn("</body>", rv)
        block = rv[rv.index("<blockquote"):rv.index("</blockquote>")]
        for tag in [
            "<cite", "</cite>", "<ol", '<li id="1"', '<li id="2"', '<li id="3"', "</ol>",
        ]:
            self.assertIn(tag, block)

    def test_context(self):
        test = "Test context & substitution"
        toml = textwrap.dedent("""
        [metadata]

        [doc]

        [doc.html]
        config = {tag_mode = "pair"}

        [doc.html.head]
        title = "{metadata[title]}"

        """)
        template = tomllib.loads(toml)
        template["metadata"]["title"] = test
        rv = Renderer().serialize(template)
        self.assertTrue(rv.startswith("<html>"))
        self.assertTrue(rv.endswith("</html>"))
        self.assertIn("<head>", rv)
        self.assertIn("</head>", rv)
        self.assertIn("<title>Test context &amp; substitution</title>", rv)


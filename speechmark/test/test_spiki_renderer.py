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

"""
https://stackoverflow.com/questions/61679282/create-web-server-using-only-standard-library
https://html.spec.whatwg.org/multipage/
"""

class RendererTests(unittest.TestCase):

    def test_head(self):
        test = "Essential head content"
        goal = textwrap.dedent(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>{test}</title>
        <head>
        </html>
        """).strip()

        toml = textwrap.dedent("""
        [doc]
        "!doctype" = "html"

        [doc.config]

        [doc.html.head]
        title = ""

        [[doc.html.head.meta]]
        """)

        template = tomllib.loads(toml)
        self.fail(goal)

    def test_doc_01(self):
        self.fail()

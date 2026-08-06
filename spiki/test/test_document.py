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

from collections import defaultdict
import mimetypes

from spiki import __version__


class Document:

    def __init__(self, *args):
        self.data = defaultdict(list)

    @property
    def header(self):
        return dict(root=id(self), format=__version__)


import pathlib
import shutil
import tempfile
import textwrap
import unittest


class DocumentTests(unittest.TestCase):

    def setUp(self):
        self.path = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.path)

    def test_simple(self):
        config = dict(port=8080)
        text = textwrap.dedent("""
        <A> Knock knock.
        <B> Who's there?
        """)
        doc = Document(config, text)
        self.assertIsInstance(doc.header, dict)
        self.assertTrue(doc.header.get("root", None))
        self.assertEqual(doc.header.get("format", None), __version__)

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

from collections import defauldict


class Document:

    def __init__(self, *args):
        self.data = defaultdict(list)

import tempfile
import unittest


class DocumentTests(unittest.TestCase):

    def test_native(self):
        a = SN(name="Alice")
        b = SN(name="Boris")
        rv = "{b.name[0]!s}".format(a=a, b=b)
        self.assertEqual(rv, "B")


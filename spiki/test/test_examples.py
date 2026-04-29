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
import string
import textwrap
import tomllib
import unittest

try:
    from string.templatelib import Interpolation
    from string.templatelib import Template
except ModuleNotFoundError:
    Interpolation = None
    Template = None


class ExampleTests(unittest.TestCase):

    @unittest.skipUnless(Interpolation, "requires Python 3.14 or later")
    def test_template(self):
        pass

#!/usr/bin/env python
#   encoding: utf-8

# Copyright (C) 2026 D E Haynes
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
import unittest

import pygments.lexers

from spiki.plugout.smk_lexer import SpeechMarkLexer


class LexerTests(unittest.TestCase):

    def setUp(self):
       self.text = importlib.resources.read_text("spiki.plugout.test", "minimum.sm")

    def test_lexer(self):
        options = {}
        lexer = pygments.lexers.get_lexer_by_name("speechmark")
        self.fail(lexer)

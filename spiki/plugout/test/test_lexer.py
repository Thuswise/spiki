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

"""

_       Generic.Strong
*       Generic.Emph
`       Generic.Prompt
#       Comment.single
{}      String.Interpol
abc     String
<ABC    Name.Variable.Global
a=1     Name.Attribute
.entrng Name.Function
.@:!    Operator
?&#,    Punctuation
1.      Punctuation.Marker
+       String.Affix

"""

import importlib.resources
import unittest

import pygments
import pygments.lexers
from pygments.token import Token

from spiki.plugout.smk_lexer import SpeechMarkLexer
from spiki.speechmark import SpeechMark


class LexerTests(unittest.TestCase):

    def setUp(self):
        self.text = importlib.resources.read_text("spiki.plugout.test", "minimum.smk")
        self.sm = SpeechMark()
        self.lexer = SpeechMarkLexer()
        # print(self.sm.loads(self.text))

    @unittest.skip("dev")
    def test_lexer(self):
        options = {}
        rv = list(pygments.lex(self.text, self.lexer))
        self.fail(rv)

    def test_text_eof(self):
        text = "Once upon a time...␃"
        rv = list(self.lexer.get_tokens_unprocessed(text))
        self.assertEqual(len(rv), 2)
        self.assertIs(Token.Other.EOT, [i[1] for i in rv][-1], rv)

    def test_simple_text(self):
        text = "Once upon a time..."
        rv = list(self.lexer.get_tokens(text, unfiltered=False))
        self.assertTrue(rv)
        self.assertNotIn(Token.Error, [i[0] for i in rv], rv)

    def test_empty_cue(self):
        text = "<> Once upon a time..."
        rv = list(self.lexer.get_tokens(text, unfiltered=False))
        self.assertNotIn(Token.Error, [i[0] for i in rv], rv)
        self.assertEqual(2, [i[0] for i in rv].count(Token.String.Affix), rv)

    def test_simple_role(self):
        text = "<ROLE> Once upon a time..."
        rv = list(self.lexer.get_tokens(text, unfiltered=False))
        self.assertNotIn(Token.Error, [i[0] for i in rv], rv)
        self.assertEqual(2, [i[0] for i in rv].count(Token.String.Affix), rv)

    def test_role_mode(self):
        text = "<ALICE:thinks>Testing times!"
        rv = list(self.lexer.get_tokens(text, unfiltered=False))
        self.assertNotIn(Token.Error, [i[0] for i in rv], rv)
        self.assertEqual(2, [i[0] for i in rv].count(Token.String.Affix), rv)
        self.assertEqual(1, [i[0] for i in rv].count(Token.Name.Variable.Global), rv)
        self.assertEqual(1, [i[0] for i in rv].count(Token.Operator), rv)

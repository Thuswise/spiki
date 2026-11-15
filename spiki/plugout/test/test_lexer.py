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
#       Comment.Single
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
import textwrap
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

    def test_lexer(self):
        options = {}
        rv = list(pygments.lex(self.text, self.lexer))
        rv = list(self.lexer.get_tokens(self.text, unfiltered=False))
        self.assertNotIn(Token.Error, [i[0] for i in rv], rv)

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

    def test_text_before_cue(self):
        text = textwrap.dedent("""
            Curtain

            <ALICE:thinks>Testing times!
            """
        ).lstrip()
        rv = list(self.lexer.get_tokens(text, unfiltered=False))
        self.assertNotIn(Token.Error, [i[0] for i in rv], rv)
        self.assertEqual(2, [i[0] for i in rv].count(Token.String.Affix), rv)
        self.assertEqual(1, [i[0] for i in rv].count(Token.Name.Variable.Global), rv)
        self.assertEqual(1, [i[0] for i in rv].count(Token.Operator), rv)

    def test_role_mode(self):
        text = "<ALICE:thinks>Testing times!"
        rv = list(self.lexer.get_tokens(text, unfiltered=False))
        tokens = [i[0] for i in rv]
        self.assertNotIn(Token.Error, tokens, rv)
        self.assertEqual(2, tokens.count(Token.String.Affix), rv)
        self.assertEqual(1, tokens.count(Token.Name.Variable.Global), rv)
        self.assertEqual(1, tokens.count(Token.Operator), rv)
        self.assertEqual(2, tokens.count(Token.Text), rv)

    def test_parameters(self):
        text = "<BORIS?pause=2> Can you help us?"
        rv = list(self.lexer.get_tokens(text, unfiltered=False))
        tokens = [i[0] for i in rv]
        self.assertNotIn(
            Token.Error,
            tokens,
            list(self.lexer.get_tokens_unprocessed(text))
        )
        self.assertEqual(2, tokens.count(Token.String.Affix), rv)
        self.assertEqual(1, tokens.count(Token.Name.Variable.Global), rv)
        self.assertEqual(1, tokens.count(Token.Operator), rv)

    def test_comments_and_left_arrows(self):
        text = textwrap.dedent("""
        <COLIN>

        # Colin is some sort of economist.
        We're < 50% lost.
        """)
        rv = list(self.lexer.get_tokens(text, unfiltered=False))
        tokens = [i[0] for i in rv]
        self.assertNotIn(Token.Error, tokens, rv)
        self.assertEqual(2, tokens.count(Token.String.Affix), rv)
        self.assertEqual(1, tokens.count(Token.Name.Variable.Global), rv)
        self.assertEqual(1, tokens.count(Token.Comment.Single), rv)
        self.assertEqual(4, tokens.count(Token.Text.Whitespace), rv)

    def test_ordered_lists(self):
        text = textwrap.dedent("""
        <BORIS#!>

        1. We're looking for the Museum
        2. Is there a Library near here?
        3. Which is the way to the river?
        """)
        rv = list(self.lexer.get_tokens(text, unfiltered=False))
        tokens = [i[0] for i in rv]
        self.assertNotIn(Token.Error, tokens, rv)
        self.assertEqual(2, tokens.count(Token.String.Affix), rv)
        self.assertEqual(1, tokens.count(Token.Name.Variable.Global), rv)
        self.assertEqual(3, tokens.count(Token.Punctuation.Marker), rv)
        self.assertEqual(5, tokens.count(Token.Text.Whitespace), rv)

    def test_unordered_lists(self):
        text = textwrap.dedent("""
        <BORIS> I looked in the bookcase before we left.

        I found:
        + `OS 219`, that's Wolverhampton,
        + The big one for Kidderminster,
        + ... and `OS 241` was missing!

        """)
        rv = list(self.lexer.get_tokens(text, unfiltered=False))
        tokens = [i[0] for i in rv]
        self.assertNotIn(Token.Error, tokens, rv)
        self.assertEqual(2, tokens.count(Token.String.Affix), rv)
        self.assertEqual(1, tokens.count(Token.Name.Variable.Global), rv)
        self.assertEqual(3, tokens.count(Token.Punctuation.Marker), rv)
        self.assertEqual(6, tokens.count(Token.Text.Whitespace), rv)

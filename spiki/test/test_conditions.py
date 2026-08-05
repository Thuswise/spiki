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

import html
import re
import textwrap
import tomllib
from types import SimpleNamespace as SN
import unittest

import spiki
from spiki.conditions import Conditions
from spiki.speechmark import SpeechMark


#TODO:
"""
Add l and u converters for upper/lower.

guard = "{B.state['into'].name[0]!u}"
value = "LON"
check = "eq" / "neq" / "in" / "nin"

"""
class Verdict:
    def evaluate(cue, context):
        return False


class ConditionalTests(unittest.TestCase):

    def test_native(self):
        a = SN(name="Alice")
        b = SN(name="Boris")
        rv = "{b.name[0]!s}".format(a=a, b=b)
        self.assertEqual(rv, "B")

    def test_cue_syntax(self):
        text = textwrap.dedent("""
        <A?guard={B.state["into"]}&value={A.state["spot"]}> Hello, {B.name}!

        """).strip()
        sm = SpeechMark()
        rv = sm.loads(text)
        self.fail(sm.cues[0])

    def test_cue_conversion_upper(self):
        text = textwrap.dedent("""
        <A?guard={B.state["into"].name!u}&value=ENGLAND}> Welcome to England, {B.name}!

        """).strip()
        sm = SpeechMark()
        rv = sm.loads(text)
        self.fail(sm.cues[0])

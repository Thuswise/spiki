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

import operator
import textwrap
from types import SimpleNamespace as SN
import unittest

from spiki.conditions import Conditions
from spiki.speechmark import SpeechMark


class ConditionsTests(unittest.TestCase):

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
        self.assertEqual(sm.cues[0]["parameters"].get("guard", [None])[0], '{B.state["into"]}')
        self.assertEqual(sm.cues[0]["parameters"].get("value", [None])[0], '{A.state["spot"]}')

    def test_cue_conversion_rot13(self):
        rv = Conditions().fix("{rude!x}", dict(rude="Ehqr!"))
        self.assertEqual(rv, "Rude!")

    def test_cue_conversion_upper(self):
        context = dict(
            B=SN(name="Boris", state={"into": SN(name="England")}),
        )
        text = textwrap.dedent("""
        <A?guard={B.state[into].name!u}&value=ENGLAND> Welcome to England, {B.name}!

        """).strip()
        c = Conditions()
        fix = c.fix(text, context)
        self.assertEqual(fix, "<A?guard=ENGLAND&value=ENGLAND> Welcome to England, Boris!")
        terms = list(c.terms(fix))
        self.assertEqual(len(terms), 1)
        cue_terms = terms[0]
        self.assertEqual(len(cue_terms), 1, terms)
        self.assertEqual(len(cue_terms[0]), 3, terms)
        self.assertEqual(cue_terms[0], ("ENGLAND", operator.eq, "ENGLAND"))
        verdict = c.verdict(text, context)
        self.assertEqual(len(verdict), len(terms))
        self.assertTrue(c.verdict(text, context)[0])

    def test_conditions_multiple_true(self):
        text = textwrap.dedent("""
        <A?guard={A.win!s}&value=True&guard={B.win!s}&value=True> Correct, {B.name}!

        """).strip()
        c = Conditions()
        v = c.verdict(text, dict(A=SN(name="A", win=True), B=SN(name="B", win=True)))
        self.assertIsInstance(v, list)
        self.assertTrue(any(v), v)
        self.assertTrue(all(v), v)
        self.assertEqual(v, [True])

    def test_cue_multiple_false(self):
        text = textwrap.dedent("""
        <A?guard={A.win!s}&value=True&guard={B.win!s}&value=True> Correct, {B.name}!

        """).strip()
        c = Conditions()
        v = c.verdict(text, dict(A=SN(name="A", win=True), B=SN(name="B", win=False)))
        self.assertIsInstance(v, list)
        self.assertEqual(v, [False])

    def test_cue_guard_no_value_true(self):
        text = textwrap.dedent("""
        <A?guard={A.win}&guard={B.win}> Correct, {B.name}!

        """).strip()
        c = Conditions()
        v = c.verdict(text, dict(A=SN(name="A", win=True), B=SN(name="B", win=True)))
        self.assertIsInstance(v, list)
        self.assertTrue(any(v), v)
        self.assertTrue(all(v), v)
        self.assertEqual(v, [True])

    def test_cue_guard_no_value_false(self):
        text = textwrap.dedent("""
        <A?guard={A.win}&guard={B.lose}> Correct, {B.name}!

        """).strip()
        c = Conditions()
        v = c.verdict(text, dict(A=SN(name="A", win=True), B=SN(name="B", win=True)))
        self.assertIsInstance(v, list)
        self.assertFalse(any(v), v)
        self.assertTrue(all(v), v)
        self.assertEqual(v, [])

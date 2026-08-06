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

import codecs
from collections.abc import Generator
import itertools
import operator
import string

from spiki.speechmark import SpeechMark


class Conditions:

    class ComparisonFormatter(string.Formatter):

        def convert_field(self, value: object, conversion: str) -> str:
            if conversion == "l":
                return str(value).lower()
            elif conversion == "u":
                return str(value).upper()
            elif conversion == "x":
                codec = codecs.lookup("rot13")
                rv, length = codec.decode(value)
                return rv
            else:
                return super().convert_field(value, conversion)

    def __init__(self):
        self.processor = SpeechMark()
        self.formatter = self.ComparisonFormatter()

    def fix(self, text: str, context: dict) -> str:
        try:
            return self.formatter.vformat(text, args=[], kwargs=context)
        except Exception as err:
            # FIXME
            raise

    def terms(self, text: str) -> Generator[list[tuple]]:
        html5 = self.processor.loads(text)
        lookup = {
            "eq": operator.eq,
        }
        for cue in self.processor.cues:
            p = cue.get("parameters", {})
            yield [
                (g, lookup.get(o, operator.eq), v)
                for g, o, v in itertools.zip_longest(p.get("guard", []), p.get("check", []), p.get("value", []))
            ]

    def verdict(self, text: dict, context: dict) -> list[bool]:
        text = self.fix(text, context)
        print(f"{text=}")
        terms = self.terms(text)
        print(f"{terms=}")
        return [all(o(g, v) for g, o, v in t) for t in terms]


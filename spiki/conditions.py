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
import logging
import operator
import string

from spiki.speechmark import SpeechMark


class Conditions:

    checks = {
        "eq": operator.eq,
        "ge": operator.ge,
        "gt": operator.gt,
        "le": operator.le,
        "lt": operator.lt,
        "ne": operator.ne,
        "is": operator.is_,
        "isnot": operator.is_not,
        "contains": operator.contains,
        "in": lambda a,b: operator.contains(b, a),
    }

    class ComparisonFormatter(string.Formatter):

        def convert_field(self, value: object, conversion: str) -> str:
            """
            Expands options for string comparisons.

            !l  lowercase
            !u  uppercase

            !1, !2, !3, !4, !5, !6, !7, !8, !9,
            !A, !B, !C, !D, !E, !F, !0: modulo 1 to 16 respectively

            !x  rot13 transformation

            """
            if conversion is None:
                return value
            elif conversion in string.hexdigits.upper():
                try:
                    mod = int(conversion, 16) or 16  # 0 means mod 16
                    return value % mod
                except TypeError as err:
                    logger = logging.getLogger("conditions")
                    logger.warning(err)
                    logger.debug(err, exc_info=True)
                return value
            elif conversion == "l":
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

    def fix(self, text: str, context: dict, hide_errors=True) -> str:
        try:
            return self.formatter.vformat(text, args=[], kwargs=context)
        except Exception as err:
            if hide_errors:
                return ""
            else:
                raise err

    def terms(self, text: str) -> Generator[list[tuple]]:
        html5 = self.processor.loads(text)
        for cue in self.processor.cues:
            p = cue.get("parameters", {})
            yield [
                (g, self.checks.get(o, operator.eq), v)
                for g, o, v in itertools.zip_longest(p.get("guard", []), p.get("check", []), p.get("value", []))
            ]

    def verdict(self, text: dict, context: dict, **kwargs) -> list[bool]:
        text = self.fix(text, context, **kwargs)
        terms = list(self.terms(text))
        return [all(o(g, g if v is None else v) for g, o, v in t) for t in terms]


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

    def evaluate(self, cue: dict, context: dict) -> list[bool]:
        return False

    def fix(self, text: str, context: dict) -> str:
        return self.formatter.vformat(text, args=[], kwargs=context)

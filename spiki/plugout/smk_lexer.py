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
import re

try:
    from pygments.lexer import RegexLexer
    from pygments.token import Keyword
    from pygments.token import Text
except ModuleNotFoundError:
    RegexLexer = object
    Keyword = object
    Text = object


class SpeechMarkLexer(RegexLexer):
    name = "SpeechMark"
    aliases = ["speechmark", "smk"]
    filenames = ["*.smk"]
    mimetypes = ["text/x-speechmark", "text/speechmark"]
    flags = re.MULTILINE

    # This lexer highlights lines that read "foo".
    tokens = {
        "root": [
            (r"foo\n", Keyword),
            (r".*\n", Text),
        ]
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


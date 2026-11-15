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

import re

try:
    from pygments.lexer import RegexLexer
    from pygments.lexer import bygroups
    from pygments.lexer import default
    from pygments.lexer import include
    from pygments.token import Name
    from pygments.token import Operator
    from pygments.token import Other
    from pygments.token import Punctuation
    from pygments.token import String
    from pygments.token import Text
    from pygments.token import Token
except ModuleNotFoundError:
    # Pygments is an optional dependency.
    # These are fake definitions to avoid import errors.
    from types import SimpleNamespace as SN
    RegexLexer = object
    Token = SN(
        Affix=None, Comment=SN(Single=None), EOT=None, Transition=None,
        Variable=SN(Global=None), Whitespace=None
    )
    Keyword = Name = Operator = Other = Punctuation = String = Text = Token
    bygroups = tuple
    default = include = str


class SpeechMarkLexer(RegexLexer):
    name = "SpeechMark"
    aliases = ["speechmark", "smk"]
    filenames = ["*.smk"]
    mimetypes = ["text/x-speechmark", "text/speechmark"]
    flags = re.MULTILINE

    """
    "expand": [
        (r"{", String.Interpol),
        (r"}(?!})", String.Affix, "#pop"),
    ],
    """
    tokens = {
        "base": [
            (r"(?=^<)", Token.Other.Transition, ("#pop", "cue")),
        ],
        "root": [
            # (r"(?={)", Token.Other.Transition, "expand"),
            include("base"),
            default("text")
        ],
        "expand": [
        ],
        "cue": [
            (r"(^<)([^.:?# >]+)", bygroups(String.Affix, Name.Variable.Global)),
            (r"^<", String.Affix),
            include("base"),
            (r"[\.=@:!]", Operator),
            (r"[\?&#]", Punctuation),
            (r"[^\.=@:!\?&# >]+", Text),
            (r">", String.Affix, ("#pop", "text")),
        ],
        "text": [
            include("base"),
            (r"\u2403", Other.EOT, ("#pop", "root")),
            (r"^\s*\+|\d+\.", Punctuation.Marker),
            (r"(?!<)\n", Text.Whitespace),
            (r"#.*?$", Token.Comment.Single),
            (r"((?!\n<|\u2403|#|^\s*\+|^\s*\d+\.).)+", Text),
        ],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


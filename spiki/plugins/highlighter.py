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


from collections import defaultdict
import itertools
from pathlib import Path
import random

import pygments
from pygments.formatters import HtmlFormatter
from pygments.lexers.html import HtmlLexer
from spiki.plugin import Change
from spiki.plugin import Plugin


class Formatter(HtmlFormatter):
    # See https://pygments.org/docs/formatters/#HtmlFormatter
    options = (
        "classprefix", "cssclass", "full",
        "anchorlinenos", "linenos", "hl_lines", "linenostart", "linenostep",
        "linenospecial", "lineseparator", "lineanchors", "linespans",
        "filename", "debug_token_types", "style", "title",
        "nowrap", "wrapcode"
    )


class Highlighter(Plugin):

    @classmethod
    def find_code(cls, node: dict):
        for k, v in node.items():
            if isinstance(v, list):
                for i in (i for i in v if isinstance(i, dict)):
                    yield from list(cls.find_code(i))
            elif isinstance(v, dict):
                yield from cls.find_code(v)

            if k == "code":
                yield node

    def __init__(self, visitor):
        super().__init__(visitor)
        self.styles = defaultdict(set)

    def run_extend(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> None | Change:
        targets = list(itertools.chain(self.find_code(node)))
        # print(HtmlFormatter().get_style_defs(".highlight"))
        for target in targets:
            lexer = HtmlLexer()
            config = target.get("config", {})
            kwargs = {k: config.pop(k) for k in list(config) if k in Formatter.options}

            # Record any style and prefix combinations for generation later
            style = kwargs.get("style", "default")
            prefix = kwargs.get("classprefix", "")
            self.styles[style].add(prefix)

            formatter = Formatter(**kwargs)
            self.logger.debug(
                f"Rendering {target}",
                extra=dict(path=path.name, phase=self.phase),
            )
            try:
                text = target.pop("code").format(**target)
            except Exception as error:
                self.logger.warning(
                    f"{type(error).__name__}: {error} ({target})",
                    extra=dict(path=path.name, phase=self.phase)
                )
                continue

            render = pygments.highlight(text, lexer, formatter)
            target["code"] = render

        return Change(self, path=path, node=node, doc=doc)

    def end_extend(self, **kwargs) -> Change:
        for style, prefixes in self.styles.items():
            path = self.visitor.root.joinpath(f"{style}.css")
            node = dict(metadata=dict(slug=path.name))
            text = ""

            self.logger.info(
                f"Generated style {path.name}",
                extra=dict(path=path.relative_to(self.visitor.root), phase=self.phase)
            )
            yield Change(self, path=path, text=text, node=node, phase=self.phase)

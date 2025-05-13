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
https://stackoverflow.com/questions/61679282/create-web-server-using-only-standard-library
https://html.spec.whatwg.org/multipage/
"""

from collections import ChainMap
from collections.abc import Generator
import copy
import enum
import html
import string
import sys
from types import SimpleNamespace
import warnings

from spiki.speechmark import SpeechMark


class Renderer:

    class Options(enum.Enum):
        tag_mode = ["open", "pair", "void"]
        block_wrap = ["div", "section", "none"]

    def __init__(self, template: dict = None, *, config: dict = None):
        self.template = template or dict()
        self.state = SimpleNamespace(attrib={}, blocks=[], config=ChainMap(config or dict()))
        self.sm = SpeechMark()

    @staticmethod
    def slugify(text, table="".maketrans({i: i for i in string.ascii_letters + string.digits + "_-"})):
        mapping = {ord(i): None for i in text}
        mapping.update(table)
        mapping[ord(" ")] = "-"
        return text.translate(mapping).lower()

    @staticmethod
    def check_config(config: dict, options: enum.Enum):
        for option in options:
            try:
                if config[option.name] not in option.value:
                    warnings.warn(f"'{config[option.name]}' is not one of {option.value}")
            except KeyError:
                continue
        return config

    def get_option(self, option: "Option"):
        rv = self.state.config.get(option.name, None)
        return rv in option.value and rv

    def walk(self, tree: dict, path: list = None, context: dict = None) -> Generator[str]:
        path = path or list()
        context = context or dict()

        self.state.attrib = tree.pop("attrib", {})
        self.state.blocks = tree.pop("blocks", [])
        self.state.config = self.state.config.new_child(self.check_config(tree.pop("config", {}), self.Options))

        attrs =  (" " + " ".join(f'{k}="{html.escape(v)}"' for k, v in self.state.attrib.items())).rstrip()
        tag_mode = self.get_option(self.Options.tag_mode)
        block_wrap = self.get_option(self.Options.block_wrap)

        try:
            tag = next(i for i in reversed(path) if isinstance(i, str))
            params = "" if isinstance(path[-1], int) and tree else attrs
            if tag_mode in ["open", "pair"]:
                yield f"<{tag}{params}>"
            elif tag_mode == "void":
                yield f"<{tag}{params} />"
        except StopIteration:
            pass

        for n, block in enumerate(self.state.blocks):
            if block_wrap:
                yield f'<{block_wrap} id="{n:02d}">'
            block = block.format(**context)
            for line in self.sm.feed(block.strip(), terminate=True):
                yield line.replace('<li id="', f'<li id="{n:02d}-')
            self.sm.reset()
            if block_wrap:
                yield f"</{block_wrap}>"

        pool = [(node, v) for node, v in tree.items() if isinstance(v, str)]
        for node, entry in pool:
            entry = html.escape(entry.format(**context))
            if tag_mode == "open":
                yield f"<{node}{attrs}>"
            elif tag_mode == "pair":
                yield f"<{node}{attrs}>{entry}</{node}>"
            elif tag_mode == "void":
                yield f"<{node}{attrs} />"

        pool = [(k, v) for k, v in tree.items() if isinstance(v, list)]
        for node, entry in pool:
            for n, item in enumerate(entry):
                yield from self.walk(item, path=path + [node, n], context=context)

        pool = [(k, v) for k, v in tree.items() if isinstance(v, dict)]
        for node, entry in pool:
            yield from self.walk(entry, path=path + [node], context=context)

        try:
            tag = next(i for i in reversed(path) if isinstance(i, str))
            if tag_mode == "pair":
                yield f"</{tag}>"
        except StopIteration:
            pass

        self.state.config.maps.pop(0)

    def serialize(self, template: dict = None) -> str:
        self.template.update(template or dict())
        context = copy.deepcopy(self.template)
        tree = context.pop("doc", dict())
        return "\n".join(filter(None, self.walk(tree, path=[], context=context)))

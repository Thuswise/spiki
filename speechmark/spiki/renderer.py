#!/usr/bin/env python
#   encoding: utf-8

# This is part of the speechmark library.
# Copyright (C) 2025 D E Haynes

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

"""
https://stackoverflow.com/questions/61679282/create-web-server-using-only-standard-library
https://html.spec.whatwg.org/multipage/
"""

from collections import ChainMap
from collections.abc import Generator
import copy
import enum
import html
import sys
from types import SimpleNamespace
import warnings

from speechmark.speechmark import SpeechMark


class Renderer:

    class Options(enum.Enum):
        tag_mode = ["open", "pair", "void"]

    def __init__(self, template: dict = None, *, config: dict = None):
        self.template = template or dict()
        self.state = SimpleNamespace(attrib={}, blocks=[], config=ChainMap(config or dict()))
        self.sm = SpeechMark()

    @classmethod
    def handle_config(cls, state, key: str, val: dict):
        for option in cls.Options:
            try:
                if val[option.name] not in option.value:
                    warnings.warn(f"{val[option.name]} is not one of {option.value}")
            except KeyError:
                continue

        state.config = state.config.new_child(val)
        return state

    def get_option(self, option: "Option"):
        rv = self.state.config[option.name]
        return rv in option.value and rv

    def walk(self, tree: dict, path: list = None, context: dict = None) -> Generator[str]:
        path = path or list()
        context = context or dict()

        # For each table:
        # + Pop config
        # + Pop attrib
        # + Pop blocks
        # For each remaining item:
        #   + Render all string values
        #   + Recurse over dict values
        #   + Recurse for each entry in list values
        self.state.attrib = tree.pop("attrib", {})
        self.state.blocks = tree.pop("blocks", [])
        self.state.config = self.state.config.new_child(tree.pop("config", {}))

        attrs =  (" " + ";".join(f'{k}="{html.escape(v)}"' for k, v in self.state.attrib.items())).rstrip()
        tag_mode = self.get_option(self.Options.tag_mode)

        try:
            tag = next(i for i in reversed(path) if isinstance(i, str))
            print(path, tag, tag_mode)
            if tag_mode in ["open", "pair"]:
                yield f"<{tag}{attrs}>"
        except StopIteration:
            pass

        pool = [(node, v) for node, v in tree.items() if isinstance(v, str)]
        for node, entry in pool:
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

    def serialize(self, template: dict = None, buf: list = None) -> str:
        self.template.update(template or dict())
        buf = buf or list()
        context = copy.deepcopy(self.template)
        tree = context.pop("doc", dict())
        for text in self.walk(tree, path=[], context=context):
            buf.append(text)
        return "\n".join(filter(None, buf))

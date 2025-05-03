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
        self.handlers = dict(
            attrib=self.handle_attrib,
            blocks=self.handle_blocks,
            config=self.handle_config,
        )
        self.state = SimpleNamespace(attrib={}, blocks=[], config=ChainMap(config or dict()))
        self.sm = SpeechMark()

    @classmethod
    def handle_attrib(cls, state, key: str, val: dict):
        state.attrib = val
        return state

    @classmethod
    def handle_blocks(cls, state, key: str, val: list):
        return state

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

    @classmethod
    def handle_dict(cls, state, key: str, val: dict):
        state.attrib = val
        return state

    @classmethod
    def handle_list(cls, state, key: str, val: list):
        return state

    def walk(self, tree: dict, path: list = None, context: dict = None) -> Generator[str]:
        path = path or list()
        context = context or dict()

        for key in list(tree):
            try:
                handler = self.handlers[key.lower()]
                val = tree.pop(key)
            except KeyError:
                continue
            else:
                self.state = handler(self.state, key, val)

        attrs =  (" " + ";".join(f'{k}="{html.escape(v)}"' for k, v in self.state.attrib.items())).rstrip()
        for key, val in (tree or dict()).items():
            if isinstance(val, dict):
                yield path, f"<{key}{attrs}>"
                self.state.attrib = {}
                yield from self.walk(val, path + [key])
                yield path, f"</{key}>"
            elif isinstance(val, list):
                for n, item in enumerate(val):
                    yield from self.walk(item, path + [key, n])
            else:
                yield path, f"<{key}{attrs}>{val}</{key}>"

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
        print(f"{tree=}", file=sys.stderr)
        self.state.attrib = tree.pop("attrib", {})
        self.state.blocks = tree.pop("blocks", [])
        self.state.config = self.state.config.new_child(tree.pop("config", {}))

        attrs =  (" " + ";".join(f'{k}="{html.escape(v)}"' for k, v in self.state.attrib.items())).rstrip()

        if path and isinstance(path[-1], str):
            yield f"<{path[-1]}{attrs}>"

        pool = [(node, v) for node, v in tree.items() if isinstance(v, str)]
        for node, entry in pool:
            yield f"<{node}{attrs}>{entry}</{node}>"

        pool = [(k, v) for k, v in tree.items() if isinstance(v, list)]
        for node, entry in pool:
            for n, item in enumerate(entry):
                yield from self.walk(item, path=path + [node, n], context=context)

        pool = [(k, v) for k, v in tree.items() if isinstance(v, dict)]
        for node, entry in pool:
            yield from self.walk(entry, path=path + [node], context=context)

        if path and isinstance(path[-1], str):
            yield f"</{path.pop(-1)}>"

    def serialize(self, template: dict = None, buf: list = None) -> str:
        self.template.update(template or dict())
        buf = buf or list()
        context = copy.deepcopy(self.template)
        tree = context.pop("doc", dict())
        for text in self.walk(tree, context=context):
            buf.append(text)
        return "\n".join(filter(None, buf))

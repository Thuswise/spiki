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
import enum
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
        self.state = SimpleNamespace(tag=None, attrib=None, config=ChainMap(config or dict()))
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

        for key, val in (tree or dict()).items():
            if isinstance(val, dict):
                # TODO: attrtibs
                yield path, f"<{key}>"
                yield from self.walk(val, path + [key])
                yield path, f"</{key}>"
            elif isinstance(val, list):
                for n, item in enumerate(val):
                    yield from self.walk(item, path + [key, n])
            else:
                yield path, f"<{key}>{val}</{key}>"

    def serialize(self, template: dict = None, buf: list = None) -> str:
        self.template.update(template or dict())
        buf = buf or list()
        context = self.template.copy()
        tree = context.pop("doc", dict())
        for path, text in self.walk(tree, context=context):
            print(path, file=sys.stderr)
            buf.append(text)
        return "\n".join(filter(None, buf))

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
from types import SimpleNamespace

from speechmark.speechmark import SpeechMark


class Renderer:

    class Options(enum.Enum):
        tag_mode = ["open", "pair", "void"]

    def __init__(self, template: dict = None, *, config: dict = None):
        self.template = template or dict()
        self.handlers = dict(
            attrib=self.handle_attrib,
            blocks=self.handle_attrib,
            config=self.handle_attrib,
        )
        self.state = SimpleNamespace(tag=None, attrib=None, config=ChainMap(config or dict()))
        self.sm = SpeechMark()

    def handle_attrib(self, key: str, val: dict):
        self.state.attrib = val
        return None

    def handle_blocks(self, key: str, val: list):
        self.sm.reset()
        return None

    def handle_config(self, key: str, val: dict):
        self.state.config = self.state.config.new_child(val)
        return None

    def handle_default(self, key: str, val: str):
        self.state.tag = key
        return val

    def walk(self, tree: dict, path: list = None, context: dict = None) -> Generator[str]:
        path = path or list()
        context = context or dict()
        for key, val in (tree or dict()).items():
            try:
                handler = self.handlers.get(key.lower(), self.handle_default)
            except AttributeError:
                handler = self.handlers.get(key, self.handle_default)

            if isinstance(val, dict):
                val = handler(key, val)
                yield from self.walk(val, path[:] + [key])
            elif isinstance(val, list):
                for n, item in enumerate(val):
                    item = handler(key, item)
                    yield from self.walk(item, path[:] + [n])
            else:
                entry = handler(key, val.format(**context))
                yield path[:] + [key], f"<{self.state.tag}>{entry}</{self.state.tag}>"

    def serialize(self, template: dict = None, buf: list = None) -> str:
        self.template.update(template or dict())
        buf = buf or list()
        context = self.template.copy()
        tree = context.pop("doc", dict())
        for path, text in self.walk(tree, context=context):
            buf.append(text)
        return "".join(filter(None, buf))

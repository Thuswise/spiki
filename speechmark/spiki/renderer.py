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


class Renderer:

    class Options(enum.Enum):
        tag_mode = ["open", "pair", "void"]

    def __init__(self, template: dict = None, *, config: dict = None):
        self.template = template or dict()
        self.config = ChainMap(config or dict())
        self.handlers = dict(
            attrib=self.handle_attrib,
            blocks=self.handle_attrib,
            config=self.handle_attrib,
        )

    def handle_attrib(self, val: dict):
        pass

    def handle_blocks(self, val: list):
        pass

    def handle_config(self, val: dict):
        pass

    def handle_default(self, val: dict):
        pass

    def walk(self, tree: dict, path: list = None) -> Generator[str]:
        path = path or list()
        for key, val in tree.items():
            if isinstance(val, dict):
                yield from self.walk(val, path[:] + [key])
            elif isinstance(val, list):
                for n, item in enumerate(val):
                    yield from self.walk(item, path[:] + [n])
            else:
                yield path[:] + [key], val

    def serialize(self, template: dict = None) -> str:
        self.template.update(template or dict())
        for node in self.walk(template):
            print(f"{node=}")
        return ""

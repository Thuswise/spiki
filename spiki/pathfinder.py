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

from collections.abc import Callable
from collections.abc import Generator
import contextlib
import datetime
import decimal
import functools
import logging
import os.path
from pathlib import Path
import shutil
import string
import tempfile
import tomllib
import warnings

from spiki.plugin import Phase
from spiki.renderer import Renderer


class Pathfinder(contextlib.ExitStack):

    @staticmethod
    def slugify(text: str, table="".maketrans({i: i for i in string.ascii_letters + string.digits + "_-"})):
        mapping = {ord(i): None for i in text}
        mapping.update(table)
        mapping[ord(" ")] = "-"
        return text.translate(mapping).lower()

    @staticmethod
    def slices(parts: tuple):
        return [tuple()] if not parts else [parts[:n] for n in range(len(parts) + 1)]

    @staticmethod
    def location_of(node: dict) -> Path:
        try:
            return node["registry"]["index"]["registry"]["path"].resolve()
        except (AttributeError, KeyError, TypeError):
            return node["registry"]["path"].resolve()

    def __init__(self, *plugins: tuple[Callable], **kwargs):
        super().__init__()
        self.indexes = dict()
        self.plugins = plugins
        self.running = None
        self.space = None
        self.logger = logging.getLogger("pathfinder")

    def __enter__(self):
        self.space = Path(tempfile.mkdtemp()).resolve()
        self.running = [self.enter_context(p) for p in self.plugins]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rv = super().__exit__(exc_type, exc_val, exc_tb)
        shutil.rmtree(self.space, ignore_errors=True)
        return rv

    def build_index(self, path: Path, root: Path = None):
        node = self.build_node(path, root=root)
        return node

    def build_node(self, path: Path, root: Path = None):
        try:
            text = path.read_text()
            node = tomllib.loads(text, parse_float=decimal.Decimal)
        except tomllib.TOMLDecodeError as error:
            self.logger.warning(f"{path}: {error}")
            raise

        node.setdefault("registry", {})["path"] = path
        node["registry"]["root"] = root
        node["registry"]["node"] = path.parent.relative_to(root).parts
        node["registry"]["time"] = datetime.datetime.now(tz=datetime.timezone.utc)

        node.setdefault("metadata", {})["slug"] = (
            node.get("metadata", {}).get("slug") or
            Pathfinder.slugify("_".join(path.relative_to(root).with_suffix("").parts))
        )
        node["metadata"]["title"] = node["metadata"].get("title", path.name)
        return node

    def merge(self, *args: tuple[dict]) -> dict:
        bases = [dict(doc=i.get("base", {})) for i in args if "base" in i]
        end = (args or [{}])[-1]
        return functools.reduce(self.update, bases + [end])

    def update(self, lhs: dict, rhs: dict) -> dict:
        "Use lhs as a base to update rhs"
        for k, v in lhs.items():
            try:
                node = rhs[k]
                if isinstance(node, dict):
                    rhs[k] = self.update(v, node)
                elif isinstance(node, list):
                    rhs[k].extend(v)
            except KeyError:
                rhs[k] = v
        return rhs

    def walk(self, *paths: list[Path], index_name="index.toml") -> Generator[tuple[Path, dict, str]]:
        paths = [i.resolve() for i in paths]
        root = Path(os.path.commonprefix(paths))
        for p in paths:
            for parent, dirnames, filenames in p.resolve().walk():
                key = parent.relative_to(root).parts
                for name in filenames:
                    if name == index_name:
                        path = parent.joinpath(name)
                        node = self.build_index(path, root=root)
                        touch = [plugin(node, phase=Phase.SURVEY) for plugin in self.running]
                        self.logger.info(
                            f"{sum(touch)} memo" + ("" if sum(touch) == 1 else "s"),
                            extra=dict(phase=Phase.SURVEY, path=path.relative_to(root).as_posix())
                        )
                        self.indexes[key] = node

            for parent, dirnames, filenames in p.resolve().walk():
                key = parent.relative_to(root).parts
                for name in filenames:
                    if name == index_name:
                        node = self.indexes[key]
                    else:
                        path = parent.joinpath(name)
                        node = self.build_node(path, root=root)

                    stack = list(filter(None, (self.indexes.get(i) for i in self.slices(key))))
                    template = self.merge(*stack + [node])

                    # TODO: call plugins
                    index = next((i for i in reversed(stack)), None)
                    if index:
                        template["registry"]["index"] = index
                        index["registry"].setdefault("nodes", []).append(node)
                        text = f"""
                        [doc.html.body]
                        config = {{tag_mode = "pair"}}
                        [[doc.html.body.nav.ul.li]]
                        attrib = {{href = "{node['metadata']['slug']}"}}
                        a = "{node['metadata']['title']}"
                        """
                        data = tomllib.loads(text)
                        rhs = self.update(data, index)

                    renderer = Renderer()
                    yield path, template, renderer.serialize(template)

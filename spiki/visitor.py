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
import copy
import dataclasses
import datetime
import decimal
import functools
import logging
from numbers import Number
import os.path
from pathlib import Path
import pkgutil
import shutil
import string
import tempfile
import tomllib
import warnings

from spiki.plugin import Change
from spiki.plugin import Phase
from spiki.renderer import Renderer


class Visitor(contextlib.ExitStack):

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

    @staticmethod
    def url_of(node: dict) -> str:
        root = node["registry"]["root"]
        parent = Visitor.location_of(node).relative_to(root).parent
        return parent.joinpath(node["metadata"]["slug"]).with_suffix(".html").as_posix()

    def __init__(self, *plugin_types: tuple[Callable], **kwargs):
        super().__init__()
        self.index_name = "index.toml"
        self.nodes = dict()
        self.state = dict()
        self.running = None
        self.space = None
        self.logger = logging.getLogger("visitor")
        self.plugins = list(filter(None, (self.init_plugin(i) for i in plugin_types)))
        self.options = kwargs

    def __enter__(self):
        self.space = Path(tempfile.mkdtemp()).resolve()
        self.running = [self.enter_context(p) for p in self.plugins]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rv = super().__exit__(exc_type, exc_val, exc_tb)
        shutil.rmtree(self.space, ignore_errors=True)
        return rv

    @property
    def root(self) -> Path:
        paths = [i.resolve() for i in self.options.get("paths", [])]
        return Path(os.path.commonprefix(paths))

    def init_plugin(self, type_name: str):
        try:
            cls = pkgutil.resolve_name(type_name)
        except (AttributeError, ModuleNotFoundError) as error:
            self.logger.warning(f"'{type_name}' not resolved. Plugin not loaded.")
            return None

        plugin = cls(self)
        return plugin

    def ancestors(self, path: Path) -> list[Path]:
        return sorted(
            (p for p in self.nodes
             if path.is_relative_to(p.parent)
             and p.name == self.index_name
            ),
            key=lambda x: len(format(x))
        )

    def build_node(self, path: Path, root: Path = None):
        # TODO: MOve to loader
        try:
            text = path.read_text()
            node = tomllib.loads(text, parse_float=decimal.Decimal)
        except tomllib.TOMLDecodeError as error:
            self.logger.warning(f"{path}: {error}")
            raise
        except UnicodeDecodeError as error:
            self.logger.warning(f"{path}: {error}")
            return None

        node.setdefault("registry", {})["path"] = path
        node["registry"]["root"] = root
        node["registry"]["node"] = path.parent.relative_to(root).parts
        node["registry"]["time"] = datetime.datetime.now(tz=datetime.timezone.utc)

        node.setdefault("metadata", {})["slug"] = (
            node.get("metadata", {}).get("slug") or
            Visitor.slugify("_".join(path.relative_to(root).with_suffix("").parts))
        )
        node["metadata"]["title"] = node["metadata"].get("title", path.name)
        return node

    def merge(self, *args: tuple[dict]) -> dict:
        bases = [dict(doc=i.get("base", {})) for i in args if "base" in i]
        end = (args or [{}])[-1]
        return functools.reduce(self.combine, bases + [end])

    def combine(self, lhs: dict, rhs: dict) -> dict:
        "Use lhs as a base to update rhs"
        for k, v in lhs.items():
            try:
                node = rhs[k]
                if isinstance(node, dict):
                    rv = self.combine(v, node)
                    lhs_keys = list(v)
                    rhs_keys = [i for i in node if i not in set(lhs_keys)]
                    rhs[k] = {k: rv[k] for k in lhs_keys + rhs_keys}
                elif isinstance(node, list):
                    rhs[k] = v + node
            except KeyError:
                rhs[k] = v
        return rhs

    def walk(self, *paths: list[Path]) -> Generator[tuple[Path, dict, str]]:
        paths = [i.resolve() for i in paths]
        for phase in [Phase.CONFIG, Phase.SURVEY]:
            for path in paths:
                try:
                    for change in filter(None, (plugin(phase, path=path) for plugin in self.running)):
                        yield dataclasses.replace(change, phase=phase)
                        self.state[change.path] = dataclasses.replace(
                            self.state.setdefault(change.path, change),
                            phase=phase,
                        )
                except Exception as error:
                    break
            else:
                for change in filter(None, (plugin(phase) for plugin in self.running)):
                    yield dataclasses.replace(change, phase=phase)

        for phase in list(Phase)[2:]:
            for path in list(self.state):
                state = self.state[path]
                try:
                    for change in filter(
                        None,
                        (
                            plugin(phase, path=path, text=state.text, node=state.node, doc=state.doc)
                            for plugin in self.running
                        )
                    ):
                        yield dataclasses.replace(change, phase=phase)
                        if change.text:
                            self.state[path].text = change.text
                        if change.node:
                            self.state[path].node.update(change.node)
                        if change.doc:
                            self.state[path].doc = change.doc
                except Exception as error:
                    self.logger.error(error, extra=dict(phase=phase), exc_info=True)
                    break
            else:
                for change in filter(None, (plugin(phase) for plugin in self.running)):
                    yield dataclasses.replace(change, phase=phase)

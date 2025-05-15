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

import argparse
from collections import ChainMap
from collections import defaultdict
from collections.abc import Generator
import datetime
import decimal
import functools
import operator
import os.path
from pathlib import Path
import shutil
import string
import sys
import tempfile
import tomllib
import warnings


class Pathfinder:

    @staticmethod
    def slugify(text: str, table="".maketrans({i: i for i in string.ascii_letters + string.digits + "_-"})):
        mapping = {ord(i): None for i in text}
        mapping.update(table)
        mapping[ord(" ")] = "-"
        return text.translate(mapping).lower()

    def __init__(self, *paths: tuple[Path]):
        self.indexes = dict()
        self.space = None

    def __enter__(self):
        self.space = Path(tempfile.mkdtemp()).resolve()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.space, ignore_errors=True)
        return self.space.exists()

    def build_index(self, path: Path, root: Path = None):
        node = self.build_node(path, root=root)
        return node

    def build_node(self, path: Path, root: Path = None):
        try:
            text = path.read_text()
            node = tomllib.loads(text, parse_float=decimal.Decimal)
        except tomllib.TOMLDecodeError as error:
            warnings.warn(f"{path}: {error}")

        node.setdefault("registry", {})["node"] = path
        node["registry"]["root"] = root
        node["registry"]["time"] = datetime.datetime.now(tz=datetime.timezone.utc)

        node.setdefault("metadata", {})["slug"] = (
            node.get("metadata", {}).get("slug") or
            Pathfinder.slugify("_".join(path.relative_to(root).with_suffix("").parts))
        )
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

    def walk(self, *paths: list[Path], index_name="index.toml") -> Generator[tuple]:
        paths = [i.resolve() for i in paths]
        root = Path(os.path.commonprefix(paths))
        for p in paths:
            for parent, dirnames, filenames in p.resolve().walk():
                key = parent.relative_to(root).parts
                for name in filenames:
                    path = parent.joinpath(name)
                    if path.name == index_name:
                        parts = path.relative_to(root).parts
                        node = self.build_index(path, root=root)
                        self.indexes[key] = node
                    else:
                        node = self.build_node(path, root=root)

                    yield node

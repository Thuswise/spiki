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
import decimal
import functools
import operator
import os.path
from pathlib import Path
import shutil
import sys
import tempfile
import tomllib
import warnings


class Pathfinder:

    @staticmethod
    def build_index(path: Path):
        try:
            text = path.read_text()
            index = tomllib.loads(text, parse_float=decimal.Decimal)
            index.setdefault("registry", {})["node"] = path
            return index
        except tomllib.TOMLDecodeError as error:
            warnings.warn(f"{path}: {error}")

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

    def merge(self, *args: tuple[dict]) -> dict:
        bases = [dict(doc=i.get("base", {})) for i in args if "base" in i]
        end = (args or [{}])[-1]
        return functools.reduce(self.update, bases + [end])

    @staticmethod
    def walk(*paths: list[Path]) -> Generator[tuple]:
        for path in paths:
            for parent, dirnames, filenames in path.resolve().walk():
                for name in filenames:
                    yield parent.joinpath(name)

    def __init__(self, *paths: tuple[Path]):
        self.state = defaultdict(ChainMap)
        self.space = None

    def __enter__(self):
        self.space = Path(tempfile.mkdtemp()).resolve()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.space, ignore_errors=True)
        return self.space.exists()

def main(args):
    paths = [i.resolve() for i in args.paths]
    root = Path(os.path.commonprefix(paths))
    for parent, dirnames, filenames in Pathfinder.walk(*paths):
        index = Pathfinder.build_index(parent, dirnames, filenames)
        if index:
            index.setdefault("registry", {})["root"] = root
            print(index)
    return 0


def parser():
    rv = argparse.ArgumentParser(usage=__doc__)
    rv.add_argument("paths", nargs="+", type=Path, help="Specify file paths")
    return rv


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()

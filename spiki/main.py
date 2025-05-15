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
import os.path
from pathlib import Path
import sys

from spiki.pathfinder import Pathfinder
from spiki.renderer import Renderer


def main(args):
    with Pathfinder() as pathfinder:
        for node in pathfinder.walk(*args.paths):
            print(node)
    print(f"{pathfinder.indexes=}")
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

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
import logging
import os.path
from pathlib import Path
import shutil
import sys

from spiki.pathfinder import Pathfinder
from spiki.renderer import Renderer

from spiki.plugin import Phase


def setup_logger():
    logging.basicConfig(level=logging.INFO)
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(
            logging.Formatter(
                fmt="{asctime}|{levelname:>8}|{phase.name:^8}| {name:<16}| {path:<32}| {message}",
                datefmt=None, style='{',
                defaults=dict(phase=Phase.CONFIG, path="")
            )
        )


def main(args):
    setup_logger()
    logger = logging.getLogger("spiki")
    args.output.mkdir(parents=True, exist_ok=True)

    plugin_types = [
        "spiki.plugins.indexer:Indexer",
    ]
    with Pathfinder(*plugin_types) as pathfinder:
        for n, (p, template, doc) in enumerate(pathfinder.walk(*args.paths)):
            destination = pathfinder.location_of(template).relative_to(template["registry"]["root"]).parent
            parent = pathfinder.space.joinpath(destination).resolve()
            parent.mkdir(parents=True, exist_ok=True)
            slug = template["metadata"]["slug"]
            path = parent.joinpath(slug).with_suffix(".html")
            path.write_text(doc)

        touch = [plugin(Phase.REPORT) for plugin in pathfinder.running]
        shutil.copytree(pathfinder.space, args.output, dirs_exist_ok=True)
    logger.info(f"Processed {n} nodes", extra=dict(phase=Phase.REPORT))
    return 0


def parser():
    default_path = Path.cwd().joinpath("output").resolve()
    rv = argparse.ArgumentParser(usage=__doc__)
    rv.add_argument("paths", nargs="+", type=Path, help="Specify file paths")
    rv.add_argument("-O", "--output", type=Path, default=default_path, help=f"Specify output directory [{default_path}]")
    return rv


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()

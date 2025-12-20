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
import http.server
import importlib.resources
import inspect
import ipaddress
import pathlib
import sys
import zipapp
import tempfile
import zipfile

try:
    from spiki.plugin import Change
    from spiki.plugin import Plugin
except (ImportError, ModuleNotFoundError):
    Change = object
    Plugin = object


class Bootstrapper(Plugin):

    def end_extend(self, **kwargs) -> Change:
        path = self.visitor.root.joinpath("__main__.py")
        node = dict(metadata=dict(slug=path.name))
        self.logger.info(f"Generating a {path.name}", extra=dict(path=path, phase=self.phase))
        return Change(self, path=path, text="#", node=node, phase=self.phase)

    def end_export(self, **kwargs) -> Change:
        path = self.visitor.root.joinpath("__main__.py")
        change = self.visitor.state[path]
        source = change.result.parent

        output = self.visitor.options["output"]
        target = output.with_suffix(".pyz")
        self.logger.info(f"Creating {target}", extra=dict(path=path, phase=self.phase))
        zipapp.create_archive(source, target=target)


def main(args):
    frozen = getattr(sys, "frozen", None)
    data = dict(inspect.getmembers(Bootstrapper))
    module = sys.modules["__main__"]
    print(data)
    print(vars(module))

    with (
        tempfile.TemporaryDirectory() as temp_dir,
        # Visitor(*plugin_types) as visitor,
    ):
        # TODO Unpack .pyz
        print(temp_dir, file=sys.stderr)

    return 0

    root = importlib.resources.files()
    for path in root.iterdir():
        print(path, type(path))
    print(f"{spec=}")
    return 0


def parser():
    rv = argparse.ArgumentParser(usage=__doc__, fromfile_prefix_chars="=")
    rv.add_argument(
        "-d", "--directory", type=pathlib.Path, default=None,
        help=f"Set the directory for source files"
    )
    rv.add_argument(
        "--host", type=ipaddress.ip_address, default=(host := ipaddress.ip_address("127.0.0.1")),
        help=f"Set the IP address to bind and serve [{host}]"
    )
    rv.add_argument(
        "--port", type=int, default=(port := 8000),
        help=f"Set the IP port [{port}]"
    )
    rv.add_argument(
        "--headless", action="store_true", default=(headless := False),
        help=f"Serve files without launching a browser [{headless}]"
    )
    rv.convert_arg_line_to_args = lambda x: x.split()
    return rv


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()

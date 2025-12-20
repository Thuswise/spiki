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
import concurrent.futures
import functools
import http.server
import importlib.resources
import ipaddress
import pathlib
import shutil
import sys
import tempfile
import time
import webbrowser
import zipapp

try:
    from spiki.plugin import Change
    from spiki.plugin import Plugin
except (ImportError, ModuleNotFoundError):
    Change = object
    Plugin = object


class Bootstrapper(Plugin):

    @staticmethod
    def get_filepath(module_name: str) -> pathlib.Path:
        module = sys.modules[module_name]
        return pathlib.Path(module.__loader__.get_filename(module_name))

    @staticmethod
    def get_source(module_name: str) -> str:
        module = sys.modules[module_name]
        return module.__loader__.get_source(module_name)

    def end_extend(self, **kwargs) -> Change:
        path = self.visitor.root.joinpath("__main__.py")
        node = dict(metadata=dict(slug=path.name))

        text = self.get_source("spiki.plugins.bootstrapper")
        self.logger.info(f"Generated the {path.name}", extra=dict(path=path, phase=self.phase))
        return Change(self, path=path, text=text, node=node, phase=self.phase)

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

    path = Bootstrapper.get_filepath("__main__")
    with (
        tempfile.TemporaryDirectory() as temp_dir,
        concurrent.futures.ThreadPoolExecutor() as executor,
    ):
        temp_path = pathlib.Path(temp_dir)
        shutil.unpack_archive(path.parent, extract_dir=temp_dir, format="zip")
        temp_path.joinpath("__main__.py").unlink(missing_ok=True)

        class LocalDirectoryMixin:
            def finish_request(self, request, client_address):
                self.RequestHandlerClass(request, client_address, self, directory=format(temp_path.resolve()))

        class HTTPDirectoryServer(LocalDirectoryMixin, http.server.ThreadingHTTPServer):
            pass

        url = f"http://{args.host}:{args.port}"
        if not args.headless:
            delay = functools.partial(time.sleep, args.delay)
            client = lambda f: webbrowser.open_new_tab(url)
            print(f"Sending client to '{url}' in {args.delay} s", file=sys.stderr)
            executor.submit(delay).add_done_callback(client)

        http.server.test(
            HandlerClass=http.server.SimpleHTTPRequestHandler,
            ServerClass=HTTPDirectoryServer,
            port=str(args.port),
            bind=format(args.host),
        )

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
    rv.add_argument(
        "--delay", type=float, default=(delay := 1.5),
        help=f"Set the delay in seconds before client connection [{delay}]"
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

import argparse
from collections import ChainMap
from collections.abc import Generator
import decimal
import pathlib
import sys
import tomllib


def walk(*paths: list[pathlib.Path]) -> Generator[tuple]:
    for path in paths:
        yield from path.resolve().walk()


def main(args):
    index_filename = "index.toml"
    print(*list(walk(*args.paths)), sep="\n")
    for node, dirnames, filenames in walk(*args.paths):
        try:
            filenames.remove(index_filename)
            index_path = node.joinpath(index_filename)
            index_text = index_path.read_text()
            index = tomllib.loads(index_text, parse_float=decimal.Decimal)
            index.setdefault("metadata", {})["node"] = index_path
            print(index)
        except ValueError:
            pass
    return 0


def parser():
    rv = argparse.ArgumentParser(usage=__doc__)
    rv.add_argument("paths", nargs="+", type=pathlib.Path, help="Specify file paths")
    return rv


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()

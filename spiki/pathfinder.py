import argparse
from collections import ChainMap
from collections import defaultdict
from collections.abc import Generator
import decimal
from pathlib import Path
import sys
import tomllib
import warnings


class Pathfinder:

    @staticmethod
    def build_index(parent: Path, dirnames: list[str], filenames: list[str], index_name="index.toml"):
        try:
            filenames.remove(index_name)
            index_path = parent.joinpath(index_name)
            index_text = index_path.read_text()
            index = tomllib.loads(index_text, parse_float=decimal.Decimal)
            index.setdefault("metadata", {})["node"] = index_path
            return index
        except tomllib.TOMLDecodeError as error:
            warnings.warn(f"{index_path}: {error}")
        except ValueError:
            pass

    @staticmethod
    def merge(*args: tuple[dict]) -> dict:
        bases = [i.get("base", {}) for i in args]
        docs = [i.get("docs", {}) for i in args]
        return base

    @staticmethod
    def walk(*paths: list[Path]) -> Generator[tuple]:
        for path in paths:
            yield from path.resolve().walk()

    def __init__(self, *paths: tuple[Path]):
        self.state = defaultdict(ChainMap)


def main(args):
    for parent, dirnames, filenames in Pathfinder.walk(*args.paths):
        index = Pathfinder.build_index(parent, dirnames, filenames)
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

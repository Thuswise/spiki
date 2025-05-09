import argparse
from collections import ChainMap
from collections import defaultdict
from collections.abc import Generator
import decimal
import functools
import operator
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

    def update(self, lhs: dict, rhs: dict) -> dict:
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
        end = (args or {}) and args[-1]
        return functools.reduce(self.update, bases + [end])

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

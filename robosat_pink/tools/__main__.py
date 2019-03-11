import os
import sys
import argparse

import shutil
import pkgutil
from importlib import import_module

import robosat_pink.tools


def main():

    if not len(sys.argv) > 1:
        print("rsp: RoboSat.pink command line tools")
        print("")
        print("Usages:")
        print("rsp -h, --help          show tools availables")
        print("rsp <tool> -h, --help   show options availables for a tool")
        print("rsp <tool> [...]        launch an rsp tool command")
        sys.exit()

    path = os.path.dirname(robosat_pink.tools.__file__)
    tools = [tool for tool in [name for _, name, _ in pkgutil.iter_modules([path]) if name != "__main__"]]
    tools = [sys.argv[1]] if sys.argv[1] in tools else tools

    os.environ["COLUMNS"] = str(shutil.get_terminal_size().columns)  # cf https://bugs.python.org/issue13041
    fc = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=40, indent_increment=1)  # noqa: E731
    parser = argparse.ArgumentParser(prog="rsp", formatter_class=fc)
    subparser = parser.add_subparsers(title="RoboSat.pink tools", metavar="")

    for tool in tools:
        module = import_module("robosat_pink.tools.{}".format(tool))
        module.add_parser(subparser, formatter_class=fc)

    args = parser.parse_args()
    args.func(args)

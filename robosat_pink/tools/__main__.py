import os
import sys
import argparse

import pkgutil
from importlib import import_module

import robosat_pink.tools


def main():

    if not len(sys.argv) > 1:
        print("rsp: RoboSat.pink command line tools")
        print("Usages:")
        print("rsp -h, --help            show tools availables")
        print("rsp <tool> -h, --help     show options for a tool")
        print("rsp <tool> [...]          launch an rsp tool command")
        sys.exit()

    path = os.path.dirname(robosat_pink.tools.__file__)
    tools = [tool for tool in [name for _, name, _ in pkgutil.iter_modules([path]) if name != "__main__"]]
    tools = [sys.argv[1]] if sys.argv[1] in tools else tools

    parser = argparse.ArgumentParser(prog="rsp")
    subparser = parser.add_subparsers(title="RoboSat.pink tools", metavar="")

    for tool in tools:
        module = import_module("robosat_pink.tools.{}".format(tool))
        module.add_parser(subparser)

    args = parser.parse_args()
    args.func(args)

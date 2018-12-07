#!/usr/bin/env python3

import os
import argparse

import pkgutil
from pathlib import Path
from importlib import import_module


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="./rsp")
    subparser = parser.add_subparsers(title="RoboSat.pink tools", metavar="")

    search_path = os.path.join(Path(__file__).parent.parent, "tools")
    tools = [name for _, name, _ in pkgutil.iter_modules(search_path) if name != "__main__"] 

    for tool in tools:
        if os.access(os.path.join(search_path, tool) + ".py", os.X_OK):
            module = import_module(tool)
            module.add_parser(subparser)

    subparser.required = True
    args = parser.parse_args()
    args.func(args)

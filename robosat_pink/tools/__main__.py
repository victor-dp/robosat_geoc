import os
import sys
import argparse

import glob
import shutil
from importlib import import_module


def main():

    if not sys.version_info >= (3, 6):
        sys.exit("ERROR: rsp needs Python 3.6 or later.")

    if not len(sys.argv) > 1:
        print("rsp: RoboSat.pink command line tools")
        print("")
        print("Usages:")
        print("rsp -h, --help          show tools availables")
        print("rsp <tool> -h, --help   show options availables for a tool")
        print("rsp <tool> [...]        launch an rsp tool command")
        sys.exit()

    tools = [os.path.basename(tool)[:-3] for tool in glob.glob(os.path.join(os.path.dirname(__file__), "[a-z]*.py"))]
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

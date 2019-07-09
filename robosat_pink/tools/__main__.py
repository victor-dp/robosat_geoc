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
    for i, arg in enumerate(sys.argv): # handle negative values cf #64
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg
    parser = argparse.ArgumentParser(prog="rsp", formatter_class=fc)
    subparser = parser.add_subparsers(title="RoboSat.pink tools", metavar="")

    for tool in tools:
        module = import_module("robosat_pink.tools.{}".format(tool))
        module.add_parser(subparser, formatter_class=fc)

    args = parser.parse_args()

    if "RSP_DEBUG" in os.environ and os.environ["RSP_DEBUG"] == "1":
        args.func(args)

    else:

        try:
            args.func(args)
        except (Exception) as error:
            sys.exit("{}ERROR: {}".format(os.linesep, error))

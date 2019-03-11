import os
import sys

import pkgutil
from pathlib import Path
from importlib import import_module


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser(
        "extract", help="Extracts GeoJSON features from OpenStreetMap .pbf", formatter_class=formatter_class
    )

    inp = parser.add_argument_group("Inputs")
    inp.add_argument("pbf", type=str, help="path to .osm.pbf file [required]")
    inp.add_argument("--type", type=str, required=True, help="type of feature to extract [required]")
    inp.add_argument("--ext_path", type=str, help="path to user's extension modules dir. Allow to use alternate types.")

    out = parser.add_argument_group("Output")
    out.add_argument("out", type=str, help="path to GeoJSON file to store features in [required]")

    parser.set_defaults(func=main)


def main(args):
    module_search_path = [args.ext_path] if args.ext_path else []
    module_search_path.append(os.path.join(Path(__file__).parent.parent, "osm"))
    modules = [(path, name) for path, name, _ in pkgutil.iter_modules(module_search_path)]
    if args.type not in [name for _, name in modules]:
        sys.exit("Unknown type, thoses available are {}".format([name for _, name in modules]))

    if args.ext_path:
        sys.path.append(args.ext_path)
        module = import_module(args.type)
    else:
        module = import_module("robosat_pink.osm.{}".format(args.type))

    handler = getattr(module, "{}Handler".format(args.type.title()))()
    handler.apply_file(filename=args.pbf, locations=True)
    handler.save(args.out)

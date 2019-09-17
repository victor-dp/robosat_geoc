import os
import sys

from robosat_pink.core import load_module


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser("extract", help="Extracts GeoJSON features from OSM .pbf", formatter_class=formatter_class)

    inp = parser.add_argument_group("Inputs")
    inp.add_argument("--type", type=str, required=True, help="type of feature to extract (e.g Building, Road) [required]")
    inp.add_argument("pbf", type=str, help="path to .osm.pbf file [required]")

    out = parser.add_argument_group("Output")
    out.add_argument("out", type=str, help="GeoJSON output file path [required]")

    parser.set_defaults(func=main)


def main(args):

    print("RoboSat.pink - extract {} from {}. Could take time.".format(args.type, args.pbf), file=sys.stderr, flush=True)

    module = load_module("robosat_pink.osm.{}".format(args.type.lower()))
    osmium_handler = getattr(module, "{}Handler".format(args.type))()
    osmium_handler.apply_file(filename=os.path.expanduser(args.pbf), locations=True)
    osmium_handler.save(os.path.expanduser(args.out))

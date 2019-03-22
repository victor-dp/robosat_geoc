import os
import sys
from importlib import import_module


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser("extract", help="Extracts GeoJSON features from OSM .pbf", formatter_class=formatter_class)

    inp = parser.add_argument_group("Inputs")
    inp.add_argument("--type", type=str, required=True, help="type of feature to extract (e.g building, road) [required]")
    inp.add_argument("pbf", type=str, help="path to .osm.pbf file [required]")

    out = parser.add_argument_group("Output")
    out.add_argument("out", type=str, help="GeoJSON output file path [required]")

    parser.set_defaults(func=main)


def main(args):

    print("RoboSat.pink - extract {} from {}.".format(args.type, args.pbf))
    print("Could take some time. Please wait.")

    try:
        module = import_module("robosat_pink.osm.{}".format(args.type))
    except:
        sys.exit("ERROR: Unknown OSM {} type extactor".format(args.type))

    try:
        osmium_handler = getattr(module, "{}Handler".format(args.type.title()))()
        osmium_handler.apply_file(filename=os.path.expanduser(args.pbf), locations=True)
    except:
        sys.exit("ERROR: Unable to extract {} from {}".format(args.type, args.pbf))

    try:
        osmium_handler.save(os.path.expanduser(args.out))
    except:
        sys.exit("ERROR: Unable to save {} in {}".format(args.type, args.out))

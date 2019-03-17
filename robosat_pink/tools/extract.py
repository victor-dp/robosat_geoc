import sys

from importlib import import_module


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser(
        "extract", help="Extracts GeoJSON features from OpenStreetMap .pbf", formatter_class=formatter_class
    )

    inp = parser.add_argument_group("Inputs")
    inp.add_argument("--type", type=str, required=True, help="type of feature to extract [required]")
    inp.add_argument("pbf", type=str, help="path to .osm.pbf file [required]")

    out = parser.add_argument_group("Output")
    out.add_argument("out", type=str, help="path to GeoJSON file to store features in [required]")

    parser.set_defaults(func=main)


def main(args):

    try:
        module = import_module("robosat_pink.osm.{}".format(args.type))
    except:
        sys.exit("Unknown OSM {} type extactor".format(args.type))

    handler = getattr(module, "{}Handler".format(args.type.title()))()
    handler.apply_file(filename=args.pbf, locations=True)
    handler.save(args.out)

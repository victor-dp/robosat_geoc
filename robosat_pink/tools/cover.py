import os
import sys
import csv
import json

from tqdm import tqdm
from mercantile import tiles
from supermercado import burntiles

from robosat_pink.datasets import tiles_from_slippy_map


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser(
        "cover", help="Generate a tiles covering, in csv format: X,Y,Z", formatter_class=formatter_class
    )

    inp = parser.add_argument_group("Inputs")
    help = "input type [default: geojson]"
    inp.add_argument("--type", type=str, default="geojson", choices=["geojson", "bbox", "dir"], help=help)
    help = "upon input type: a geojson file path, a lat/lon bbox or a XYZ tiles dir path [required]"
    inp.add_argument("input", type=str, help=help)

    out = parser.add_argument_group("Outputs")
    out.add_argument("--zoom", type=int, help="zoom level of tiles [required for geojson or bbox modes]")
    out.add_argument("out", type=str, help="cover csv file output path [required]")

    parser.set_defaults(func=main)


def main(args):

    if not args.zoom and args.type in ["geojson", "bbox"]:
        sys.exit("Zoom parameter is required")

    cover = []

    if args.type == "geojson":
        with open(args.input) as f:
            features = json.load(f)

        for feature in tqdm(features["features"], ascii=True, unit="feature"):
            cover.extend(map(tuple, burntiles.burn([feature], args.zoom).tolist()))

        cover = list(set(cover))  # tiles can overlap for multiple features; unique tile ids

    elif args.type == "bbox":
        west, south, east, north = map(float, args.input.split(","))
        cover = tiles(west, south, east, north, args.zoom)

    elif args.type == "dir":
        cover = [tile for tile, _ in tiles_from_slippy_map(args.input)]

    if os.path.dirname(args.out) and not os.path.isdir(os.path.dirname(args.out)):
        os.makedirs(os.path.dirname(args.out), exist_ok=True)

    with open(args.out, "w") as fp:
        csv.writer(fp).writerows(cover)

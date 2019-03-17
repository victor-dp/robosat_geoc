import os
import sys
import csv
import json
import math

from tqdm import tqdm
from random import shuffle
from mercantile import tiles
from supermercado import burntiles

from robosat_pink.datasets import tiles_from_slippy_map


def add_parser(subparser, formatter_class):

    parser = subparser.add_parser(
        "cover", help="Generate a tiles covering, in csv format: X,Y,Z", formatter_class=formatter_class
    )

    inp = parser.add_argument_group("Inputs")
    inp.add_argument(
        "--type", type=str, default="geojson", choices=["geojson", "bbox", "dir"], help="input type [default: geojson]"
    )
    inp.add_argument(
        "input", type=str, help="upon input type: a geojson file path, a lat/lon bbox or a XYZ tiles dir path [required]"
    )

    out = parser.add_argument_group("Outputs")
    out.add_argument("--zoom", type=int, help="zoom level of tiles [required for geojson or bbox modes]")
    out.add_argument("--splits", type=str, help="if set, shuffle and split in several cover pieces. [e.g 50,15,35]")
    out.add_argument("out", type=str, nargs="+", help="cover csv output paths [required]")

    parser.set_defaults(func=main)


def main(args):

    if not args.zoom and args.type in ["geojson", "bbox"]:
        sys.exit("ERROR: Zoom parameter is required.")

    if args.splits:

        try:
            splits = [int(split) for split in args.splits.split(",")]
            assert len(splits) == len(args.out)
            assert sum(splits) == 100
        except:
            sys.exit("ERROR: Invalid split value or incoherent with provided out paths.")

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

    if args.splits:
        shuffle(cover)  # in-place
        splits = [math.floor(len(cover) * split / 100) for i, split in enumerate(splits, 1)]
        s = 0
        covers = []
        for e in splits:
            covers.append(cover[s : s + e - 1])
            s += e
    else:
        covers = [cover]

    for i, cover in enumerate(covers):

        if os.path.dirname(args.out[i]) and not os.path.isdir(os.path.dirname(args.out[i])):
            os.makedirs(os.path.dirname(args.out[i]), exist_ok=True)

        with open(args.out[i], "w") as fp:
            csv.writer(fp).writerows(cover)

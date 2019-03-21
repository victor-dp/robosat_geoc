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

    inp = parser.add_argument_group("Input [one among the following is required]")
    inp.add_argument("--dir", type=str, help="XYZ tiles dir path")
    inp.add_argument("--bbox", type=str, help="a lat/lon bbox [e.g  4.2,45.1,5.4,46.3]")
    inp.add_argument("--geojson", type=str, help="a geojson file path")

    out = parser.add_argument_group("Outputs")
    out.add_argument("--zoom", type=int, help="zoom level of tiles [required with --geojson or --bbox]")
    out.add_argument("--splits", type=str, help="if set, shuffle and split in several cover subpieces. [e.g 50,15,35]")
    out.add_argument("out", type=str, nargs="+", help="cover csv output paths [required]")

    parser.set_defaults(func=main)


def main(args):

    if int(args.bbox != None) + int(args.geojson != None) + int(args.dir != None) != 1:
        sys.exit("ERROR: One, and only one, input type must be provided, among: --dir, --bbox or --geojson.")

    if args.bbox:
        try:
            west, south, east, north = map(float, args.bbox.split(","))
        except:
            sys.exit("ERROR: invalid bbox parameter.")

    if args.splits:

        try:
            splits = [int(split) for split in args.splits.split(",")]
            assert len(splits) == len(args.out)
            assert sum(splits) == 100
        except:
            sys.exit("ERROR: Invalid split value or incoherent with provided out paths.")

    if not args.zoom and (args.geojson or args.bbox):
        sys.exit("ERROR: Zoom parameter is required.")

    cover = []

    if args.geojson:
        with open(args.geojson) as f:
            features = json.load(f)

        try:
            for feature in tqdm(features["features"], ascii=True, unit="feature"):
                cover.extend(map(tuple, burntiles.burn([feature], args.zoom).tolist()))
        except:
            sys.exit("ERROR: invalid or unsupported GeoJSON.")

        cover = list(set(cover))  # tiles can overlap for multiple features; unique tile ids

    if args.bbox:
        cover = tiles(west, south, east, north, args.zoom)

    if args.dir:
        cover = [tile for tile, _ in tiles_from_slippy_map(args.dir)]

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

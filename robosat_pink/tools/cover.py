import os
import sys
import csv
import json
import math

from tqdm import tqdm
from random import shuffle
from mercantile import tiles, xy_bounds
from supermercado import burntiles
from rasterio import open as rasterio_open
from rasterio.warp import transform_bounds

from robosat_pink.tiles import tiles_from_slippy_map, tiles_from_csv


def add_parser(subparser, formatter_class):

    parser = subparser.add_parser(
        "cover", help="Generate a tiles covering, in csv format: X,Y,Z", formatter_class=formatter_class
    )

    inp = parser.add_argument_group("Input [one among the following is required]")
    inp.add_argument("--dir", type=str, help="XYZ tiles dir path")
    inp.add_argument("--bbox", type=str, help="a lat/lon bbox: xmin,ymin,xmax,ymax or a bbox: xmin,xmin,xmax,xmax,EPSG:xxxx")
    inp.add_argument("--geojson", type=str, help="a geojson file path")
    inp.add_argument("--cover", type=str, help="a cover file path")
    inp.add_argument("--raster", type=str, help="a raster file path")

    out = parser.add_argument_group("Outputs")
    out.add_argument("--zoom", type=int, help="zoom level of tiles [required with --geojson or --bbox]")
    out.add_argument("--splits", type=str, help="if set, shuffle and split in several cover subpieces. [e.g 50/15/35]")
    out.add_argument("out", type=str, nargs="+", help="cover csv output paths [required]")

    parser.set_defaults(func=main)


def main(args):

    if (
        int(args.bbox is not None)
        + int(args.geojson is not None)
        + int(args.dir is not None)
        + int(args.raster is not None)
        + int(args.cover is not None)
        != 1
    ):
        sys.exit("ERROR: One, and only one, input type must be provided, among: --dir, --bbox, --cover or --geojson.")

    if args.bbox:
        try:
            w, s, e, n, crs = args.bbox.split(",")
            w, s, e, n = map(float, (w, s, e, n))
        except:
            try:
                crs = None
                w, s, e, n = map(float, args.bbox.split(","))
            except:
                sys.exit("ERROR: invalid bbox parameter.")

    if args.splits:

        try:
            splits = [int(split) for split in args.splits.split("/")]
            assert len(splits) == len(args.out)
            assert sum(splits) == 100
        except:
            sys.exit("ERROR: Invalid split value or incoherent with provided out paths.")

    if not args.zoom and (args.geojson or args.bbox or args.raster):
        sys.exit("ERROR: Zoom parameter is required.")

    args.out = [os.path.expanduser(out) for out in args.out]

    cover = []

    if args.raster:
        print("RoboSat.pink - cover from {} at zoom {}".format(args.raster, args.zoom))
        with rasterio_open(os.path.expanduser(args.raster)) as r:
            try:
                w, s, e, n = transform_bounds(r.crs, "EPSG:4326", *r.bounds)
            except:
                sys.exit("ERROR: unable to deal with raster projection")

            cover = tiles(w, s, e, n, args.zoom)

    if args.geojson:
        print("RoboSat.pink - cover from {} at zoom {}".format(args.geojson, args.zoom))
        with open(os.path.expanduser(args.geojson)) as f:
            features = json.load(f)

        try:
            for feature in tqdm(features["features"], ascii=True, unit="feature"):
                cover.extend(map(tuple, burntiles.burn([feature], args.zoom).tolist()))
        except:
            sys.exit("ERROR: invalid or unsupported GeoJSON.")

        cover = list(set(cover))  # tiles can overlap for multiple features; unique tile ids

    if args.bbox:
        print("RoboSat.pink - cover from {} at zoom {}".format(args.bbox, args.zoom))
        if crs:
            try:
                w, s, e, n = transform_bounds(crs, "EPSG:4326", w, s, e, n)
            except:
                sys.exit("ERROR: unable to deal with raster projection")

        cover = tiles(w, s, e, n, args.zoom)

    if args.dir:
        print("RoboSat.pink - cover from {}".format(args.dir))
        cover = [tile for tile, _ in tiles_from_slippy_map(args.dir)]

    if args.cover:
        print("RoboSat.pink - cover from {}".format(args.cover))
        cover = [tile for tile in tiles_from_csv(args.cover)]

    _cover = []
    for tile in tqdm(cover, ascii=True, unit="tile"):
        if args.zoom and tile.z != args.zoom:
            w, s, n, e = transform_bounds("EPSG:3857", "EPSG:4326", *xy_bounds(tile))
            for t in tiles(w, s, n, e, args.zoom):
                unique = True
                for _t in _cover:
                    if _t == t:
                        unique = False
                if unique:
                    _cover.append(t)
        else:
            _cover.append(tile)
    cover = _cover

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

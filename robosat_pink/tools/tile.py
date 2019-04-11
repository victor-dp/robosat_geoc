import os
import sys
import math
from tqdm import tqdm
import concurrent.futures as futures

import numpy as np

import shutil
import mercantile

from rasterio import open as rasterio_open
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds, calculate_default_transform
from rasterio.transform import from_bounds

from robosat_pink.config import load_config, check_classes
from robosat_pink.tiles import (
    tile_image_to_file,
    tile_label_to_file,
    tile_from_slippy_map,
    tile_image_from_file,
    tile_label_from_file,
)
from robosat_pink.colors import make_palette
from robosat_pink.web_ui import web_ui


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser("tile", help="Tile a raster, or a rasters coverage", formatter_class=formatter_class)

    inp = parser.add_argument_group("Inputs")
    inp.add_argument("rasters", type=str, nargs="+", help="path to raster files to tile [required]")

    out = parser.add_argument_group("Output")
    out.add_argument("--zoom", type=int, required=True, help="zoom level of tiles [required]")
    out.add_argument("--ts", type=int, default=512, help="tile size in pixels [default: 512]")
    out.add_argument("out", type=str, help="output directory path [required]")

    lab = parser.add_argument_group("Labels")
    lab.add_argument("--label", action="store_true", help="if set, generate label tiles")
    lab.add_argument("--config", type=str, help="path to config file [required in label mode]")

    perf = parser.add_argument_group("Performances")
    perf.add_argument("--workers", type=int, help="number of workers [default: CPU / 2]")

    ui = parser.add_argument_group("Web UI")
    ui.add_argument("--web_ui_base_url", type=str, help="alternate Web UI base URL")
    ui.add_argument("--web_ui_template", type=str, help="alternate Web UI template path")
    ui.add_argument("--no_web_ui", action="store_true", help="desactivate Web UI output")

    parser.set_defaults(func=main)


def is_nodata(image, no_data=0, threshold=5):

    if (
        np.all(image[0, :, :] == no_data)
        or np.all(image[-1, :, :] == no_data)
        or np.all(image[:, 0, :] == no_data)
        or np.all(image[:, -1, :] == no_data)
    ):
        return True  # pixel border is no_data, on all bands

    C, W, H = image.shape
    return np.sum(image[:, :, :] == no_data) > ((threshold * C * 100) / (W * H))


def main(args):

    if not args.workers:
        args.workers = max(1, math.floor(os.cpu_count() * 0.5))

    if args.label:
        config = load_config(args.config)
        check_classes(config)
        colors = [classe["color"] for classe in config["classes"]]
        palette = make_palette(*colors)

    splits_path = os.path.join(os.path.expanduser(args.out), ".splits")
    tiles_map = {}

    print("RoboSat.pink - tile on CPU, with {} workers".format(args.workers))

    bands = -1
    for path in args.rasters:
        try:
            raster = rasterio_open(path)
            w, s, e, n = transform_bounds(raster.crs, "EPSG:4326", *raster.bounds)
        except:
            sys.exit("Error: Unable to load raster {} or deal with it's projection".format(args.raster))

        if bands != -1:
            assert bands == len(raster.indexes), "Coverage must be bands consistent"
        bands = len(raster.indexes)

        tiles = [mercantile.Tile(x=x, y=y, z=z) for x, y, z in mercantile.tiles(w, s, e, n, args.zoom)]
        for tile in tiles:
            tile_key = (str(tile.x), str(tile.y), str(tile.z))
            if tile_key not in tiles_map.keys():
                tiles_map[tile_key] = []
            tiles_map[tile_key].append(path)

    if args.label:
        ext = "png"
        bands = 1
    if not args.label:
        if bands == 1:
            ext = "png"
        if bands == 3:
            ext = "webp"
        if bands > 3:
            ext = "tiff"

    tiles = []
    progress = tqdm(total=len(tiles_map), ascii=True, unit="tile")
    # Begin to tile plain tiles
    with futures.ThreadPoolExecutor(args.workers) as executor:

        def worker(path):

            raster = rasterio_open(path)
            w, s, e, n = transform_bounds(raster.crs, "EPSG:4326", *raster.bounds)
            transform, _, _ = calculate_default_transform(raster.crs, "EPSG:3857", raster.width, raster.height, w, s, e, n)
            tiles = [mercantile.Tile(x=x, y=y, z=z) for x, y, z in mercantile.tiles(w, s, e, n, args.zoom)]
            tiled = []

            for tile in tiles:

                try:
                    w, s, e, n = mercantile.xy_bounds(tile)

                    # inspired by rio-tiler, cf: https://github.com/mapbox/rio-tiler/pull/45
                    warp_vrt = WarpedVRT(
                        raster,
                        crs="epsg:3857",
                        resampling=Resampling.bilinear,
                        add_alpha=False,
                        transform=from_bounds(w, s, e, n, args.ts, args.ts),
                        width=math.ceil((e - w) / transform.a),
                        height=math.ceil((s - n) / transform.e),
                    )
                    data = warp_vrt.read(
                        out_shape=(len(raster.indexes), args.ts, args.ts), window=warp_vrt.window(w, s, e, n)
                    )
                    image = np.moveaxis(data, 0, 2)  # C,H,W -> H,W,C
                except:
                    sys.exit("Error: Unable to tile {} from raster {}.".format(str(tile), raster))

                tile_key = (str(tile.x), str(tile.y), str(tile.z))
                if not args.label and len(tiles_map[tile_key]) == 1 and is_nodata(image):
                    progress.update()
                    continue

                if len(tiles_map[tile_key]) > 1:
                    out = os.path.join(splits_path, str(tiles_map[tile_key].index(path)))
                else:
                    out = args.out

                x, y, z = map(int, tile)

                if not args.label:
                    ret = tile_image_to_file(out, mercantile.Tile(x=x, y=y, z=z), image)
                if args.label:
                    ret = tile_label_to_file(out, mercantile.Tile(x=x, y=y, z=z), palette, image)

                if not ret:
                    sys.exit("Error: Unable to write tile {} from raster {}.".format(str(tile), raster))

                if len(tiles_map[tile_key]) == 1:
                    progress.update()
                    tiled.append(mercantile.Tile(x=x, y=y, z=z))

            return tiled

        for tiled in executor.map(worker, args.rasters):
            if tiled is not None:
                tiles.extend(tiled)

    # Aggregate remaining tiles splits
    with futures.ThreadPoolExecutor(args.workers) as executor:

        def worker(tile_key):

            if len(tiles_map[tile_key]) == 1:
                return

            image = np.zeros((args.ts, args.ts, bands), np.uint8)

            x, y, z = map(int, tile_key)
            for i in range(len(tiles_map[tile_key])):
                root = os.path.join(splits_path, str(i))
                _, path = tile_from_slippy_map(root, x, y, z)

                if not args.label:
                    split = tile_image_from_file(path)
                if args.label:
                    split = tile_label_from_file(path)
                    split = split.reshape((args.ts, args.ts, 1))  # H,W -> H,W,C

                assert image.shape == split.shape
                image[:, :, :] += split[:, :, :]

            if not args.label and is_nodata(image):
                progress.update()
                return

            tile = mercantile.Tile(x=x, y=y, z=z)

            if not args.label:
                ret = tile_image_to_file(args.out, tile, image)

            if args.label:
                ret = tile_label_to_file(args.out, tile, palette, image)

            if not ret:
                sys.exit("Error: Unable to write tile {}.".format(str(tile_key)))

            progress.update()
            return tile

        for tiled in executor.map(worker, tiles_map.keys()):
            if tiled is not None:
                tiles.append(tiled)

        if splits_path and os.path.isdir(splits_path):
            shutil.rmtree(splits_path)  # Delete suffixes dir if any

    if not args.no_web_ui:
        template = "leaflet.html" if not args.web_ui_template else args.web_ui_template
        base_url = args.web_ui_base_url if args.web_ui_base_url else "./"
        web_ui(args.out, base_url, tiles, tiles, ext, template)

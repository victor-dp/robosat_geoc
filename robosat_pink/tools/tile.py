import os
import sys
import math
from tqdm import tqdm

import numpy as np
from PIL import Image

import mercantile

from rasterio import open as rasterio_open
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds, calculate_default_transform
from rasterio.transform import from_bounds

from robosat_pink.config import load_config, check_classes
from robosat_pink.colors import make_palette
from robosat_pink.web_ui import web_ui


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser("tile", help="Tile a raster", formatter_class=formatter_class)

    inp = parser.add_argument_group("Inputs")
    inp.add_argument("raster", type=str, help="path to the raster to tile [required]")
    inp.add_argument("--config", type=str, help="path to config file [required if RSP_CONFIG env var is not set]")
    inp.add_argument("--no_data", type=int, help="color considered as no data [0-255]. If set, skip related tile")

    out = parser.add_argument_group("Output")
    choices = ["image", "label"]
    out.add_argument("out", type=str, help="output directory path [required]")
    out.add_argument("--type", type=str, choices=choices, default="image", help="image or label tiling [default: image]")
    out.add_argument("--zoom", type=int, required=True, help="zoom level of tiles [required]")
    out.add_argument("--tile_size", type=int, default=512, help="tile size in pixels [default: 512]")

    ui = parser.add_argument_group("Web UI")
    ui.add_argument("--web_ui_base_url", type=str, help="alternate Web UI base URL")
    ui.add_argument("--web_ui_template", type=str, help="alternate Web UI template path")
    ui.add_argument("--no_web_ui", action="store_false", help="desactivate Web UI output")

    parser.set_defaults(func=main)


def main(args):

    config = load_config(args.config)
    check_classes(config)
    colors = [classe["color"] for classe in config["classes"]]
    tile_size = args.tile_size
    tiles_nodata = []

    print("RoboSat.pink - tile raster {}".format(args.raster))

    try:
        raster = rasterio_open(args.raster)
        w, s, e, n = bounds = transform_bounds(raster.crs, "EPSG:4326", *raster.bounds)
        transform, _, _ = calculate_default_transform(raster.crs, "EPSG:3857", raster.width, raster.height, *bounds)
        tiles = [mercantile.Tile(x=x, y=y, z=z) for x, y, z in mercantile.tiles(w, s, e, n, args.zoom)]
    except:
        sys.exit("Error: Unable to load raster {} or deal with it's projection".format(args.raster))

    for tile in tqdm(tiles, desc="Tiling", unit="tile", ascii=True):

        #try:
        w, s, e, n = mercantile.xy_bounds(tile)

        # inspired by rio-tiler, cf: https://github.com/mapbox/rio-tiler/pull/45
        warp_vrt = WarpedVRT(
            raster,
            crs="epsg:3857",
            resampling=Resampling.bilinear,
            add_alpha=False,
            transform=from_bounds(w, s, e, n, args.tile_size, args.tile_size),
            width=math.ceil((e - w) / transform.a),
            height=math.ceil((s - n) / transform.e),
        )
        data = warp_vrt.read(out_shape=(len(raster.indexes), tile_size, tile_size), window=warp_vrt.window(w, s, e, n))

        #except:
        #    sys.exit("Error: Unable to tile {} from raster {}.".format(str(tile), args.raster))

        # If no_data is set, remove all tiles with at least one whole border filled only with no_data (on all bands)
        if type(args.no_data) is not None and (
            np.all(data[:, 0, :] == args.no_data)
            or np.all(data[:, -1, :] == args.no_data)
            or np.all(data[:, :, 0] == args.no_data)
            or np.all(data[:, :, -1] == args.no_data)
        ):
            tiles_nodata.append(tile)
            continue

        path = os.path.join(args.out, str(args.zoom), str(tile.x), str(tile.y))
        try:
            os.makedirs(os.path.join(args.out, str(args.zoom), str(tile.x)), exist_ok=True)

            C, W, H = data.shape

            if args.type == "label":
                assert C == 1, "Error: Label raster input should be 1 band"  # FIXME: cf #8

                ext = "png"
                img = Image.fromarray(np.squeeze(data, axis=0), mode="P")
                img.putpalette(make_palette(colors[0], colors[1]))
                img.save("{}.{}".format(path, ext), optimize=True)

            elif args.type == "image":
                assert C == 1 or C == 3, "Error: Image raster input should be either 1 or 3 bands"

                # GeoTiff could be 16 or 32bits
                if data.dtype == "uint16":
                    data = np.uint8(data / 256)
                elif data.dtype == "uint32":
                    data = np.uint8(data / (256 * 256))

                if C == 1:
                    ext = "png"
                    Image.fromarray(np.squeeze(data, axis=0), mode="L").save("{}.{}".format(path, ext), optimize=True)
                elif C == 3:
                    ext = "webp"
                    Image.fromarray(np.moveaxis(data, 0, 2), mode="RGB").save("{}.{}".format(path, ext), optimize=True)
        except:
            sys.exit("Error: Unable to write tile {}".format(path))

    if not args.no_web_ui:
        template = "leaflet.html" if not args.web_ui_template else args.web_ui_template
        tiles = [tile for tile in tiles if tile not in tiles_nodata]
        base_url = args.web_ui_base_url if args.web_ui_base_url else "./"
        web_ui(args.out, base_url, tiles, tiles, ext, template)

import sys
from tqdm import tqdm

import numpy as np
from PIL import Image

import json
import mercantile
import rasterio.features
import rasterio.transform

from robosat_pink.config import load_config
from robosat_pink.tiles import tiles_from_slippy_map


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser(
        "vectorize", help="Extract simplified GeoJSON features from segmentation masks", formatter_class=formatter_class
    )

    inp = parser.add_argument_group("Inputs")
    inp.add_argument("masks", type=str, help="input masks directory path [required]")
    inp.add_argument("--type", type=str, required=True, help="type of features to extract (i.e class title) [required]")
    inp.add_argument("--config", type=str, required=True, help="path to configuration file [required]")

    out = parser.add_argument_group("Outputs")
    out.add_argument("out", type=str, help="path to GeoJSON file to store features in [required]")

    parser.set_defaults(func=main)


def main(args):
    config = load_config(args.config)
    tile_size = config["model"]["tile_size"]
    index = [i for i in (list(range(len(config["classes"])))) if config["classes"][i]["title"] == args.type]
    if not index:
        sys.exit("Error: Requested type not found among classes title in the config file.")

    with open(args.out, "w", encoding="utf-8") as out:
        first = True
        out.write('{"type":"FeatureCollection","features":[')

        for tile, path in tqdm(list(tiles_from_slippy_map(args.masks)), ascii=True, unit="mask"):
            features = (np.array(Image.open(path).convert("P"), dtype=np.uint8) == index).astype(np.uint8)
            transform = rasterio.transform.from_bounds((*mercantile.bounds(tile.x, tile.y, tile.z)), tile_size, tile_size)

            for shape, value in rasterio.features.shapes(features, transform=transform):
                prop = '"properties":{{"x":{},"y":{},"z":{}}}'.format(int(tile.x), int(tile.y), int(tile.z))
                geom = '"geometry":{{"type": "Polygon", "coordinates":{}}}'.format(json.dumps(shape["coordinates"]))
                out.write('{}{{"type":"Feature",{},{}}}'.format("," if not first else "", geom, prop))
                first = False

        out.write("]}")

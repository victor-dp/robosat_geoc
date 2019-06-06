import os
import sys
import math
import json
import torch
import concurrent.futures as futures

from PIL import Image
from tqdm import tqdm
import numpy as np

from mercantile import feature

from robosat_pink.core import web_ui, Logs
from robosat_pink.tiles import tiles_from_slippy_map, tile_from_slippy_map, tile_image_from_file, tile_image_to_file
from robosat_pink.metrics.qod import get as compare


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser(
        "compare",
        help="Compute composite images and/or metrics to compare several XYZ dirs",
        formatter_class=formatter_class,
    )

    inp = parser.add_argument_group("Inputs")
    choices = ["side", "stack", "list"]
    inp.add_argument("--mode", type=str, default="side", choices=choices, help="compare mode [default: side]")
    inp.add_argument("--labels", type=str, help="path to tiles labels directory [required for QoD filtering]")
    inp.add_argument("--masks", type=str, help="path to tiles masks directory [required for QoD filtering)")
    inp.add_argument("--images", type=str, nargs="+", help="path to images directories [required for stack or side modes]")
    inp.add_argument("--workers", type=int, help="number of workers [default: CPU / 2]")

    qod = parser.add_argument_group("QoD Filtering")
    qod.add_argument("--minimum_fg", type=float, default=0.0, help="skip tile if label foreground below. [default: 0]")
    qod.add_argument("--maximum_fg", type=float, default=100.0, help="skip tile if label foreground above [default: 100]")
    qod.add_argument("--minimum_qod", type=float, default=0.0, help="skip tile if QoD metric below [default: 0]")
    qod.add_argument("--maximum_qod", type=float, default=100.0, help="skip tile if QoD metric above [default: 100]")

    out = parser.add_argument_group("Outputs")
    out.add_argument("--vertical", action="store_true", help="output vertical image aggregate [optionnal for side mode]")
    out.add_argument("--geojson", action="store_true", help="output results as GeoJSON [optionnal for list mode]")
    out.add_argument("--format", type=str, default="webp", help="output images file format [default: webp]")
    out.add_argument("out", type=str, help="output path")

    ui = parser.add_argument_group("Web UI")
    ui.add_argument("--web_ui_base_url", type=str, help="alternate Web UI base URL")
    ui.add_argument("--web_ui_template", type=str, help="alternate Web UI template path")
    ui.add_argument("--no_web_ui", action="store_true", help="desactivate Web UI output")

    parser.set_defaults(func=main)


def main(args):

    args.out = os.path.expanduser(args.out)

    if not args.workers:
        args.workers = max(1, math.floor(os.cpu_count() * 0.5))

    print("RoboSat.pink - compare {} on CPU, with {} workers".format(args.mode, args.workers))

    if not args.masks or not args.labels:
        if args.mode == "list":
            sys.exit("ERROR: Parameters masks and labels are mandatories in list mode.")
        if args.minimum_fg > 0 or args.maximum_fg < 100 or args.minimum_qod > 0 or args.maximum_qod < 100:
            sys.exit("ERROR: Parameters masks and labels are mandatories in QoD filtering.")

    try:
        if args.images:
            tiles = [tile for tile, _ in tiles_from_slippy_map(args.images[0])]
            for image in args.images[1:]:
                assert sorted(tiles) == sorted([tile for tile, _ in tiles_from_slippy_map(image)])

        if args.labels and args.masks:
            tiles_masks = [tile for tile, _ in tiles_from_slippy_map(args.masks)]
            tiles_labels = [tile for tile, _ in tiles_from_slippy_map(args.labels)]
            if args.images:
                assert sorted(tiles) == sorted(tiles_masks) == sorted(tiles_labels)
            else:
                assert sorted(tiles_masks) == sorted(tiles_labels)
                tiles = tiles_masks
    except:
        sys.exit("ERROR: inconsistent input coverage")

    tiles_list = []
    tiles_compare = []
    progress = tqdm(total=len(tiles), ascii=True, unit="tile")
    log = False if args.mode == "list" else Logs(os.path.join(args.out, "log"))

    with futures.ThreadPoolExecutor(args.workers) as executor:

        def worker(tile):
            x, y, z = list(map(str, tile))

            if args.masks and args.labels:

                label = np.array(Image.open(os.path.join(args.labels, z, x, "{}.png".format(y))))
                mask = np.array(Image.open(os.path.join(args.masks, z, x, "{}.png".format(y))))

                assert label.shape == mask.shape

                try:
                    dist, fg_ratio, qod = compare(torch.as_tensor(label, device="cpu"), torch.as_tensor(mask, device="cpu"))
                except:
                    progress.update()
                    return False, tile

                if not args.minimum_fg <= fg_ratio <= args.maximum_fg or not args.minimum_qod <= qod <= args.maximum_qod:
                    progress.update()
                    return True, tile

            tiles_compare.append(tile)

            if args.mode == "side":
                for i, root in enumerate(args.images):
                    img = tile_image_from_file(tile_from_slippy_map(root, x, y, z)[1])

                    if i == 0:
                        side = np.zeros((img.shape[0], img.shape[1] * len(args.images), 3))
                        side = np.swapaxes(side, 0, 1) if args.vertical else side
                        image_shape = img.shape
                    else:
                        assert image_shape[0:2] == img.shape[0:2], "Unconsistent image size to compare"

                    if args.vertical:
                        side[i * image_shape[0] : (i + 1) * image_shape[0], :, :] = img
                    else:
                        side[:, i * image_shape[0] : (i + 1) * image_shape[0], :] = img

                tile_image_to_file(args.out, tile, np.uint8(side))

            elif args.mode == "stack":
                for i, root in enumerate(args.images):
                    tile_image = tile_image_from_file(tile_from_slippy_map(root, x, y, z)[1])

                    if i == 0:
                        image_shape = tile_image.shape[0:2]
                        stack = tile_image / len(args.images)
                    else:
                        assert image_shape == tile_image.shape[0:2], "Unconsistent image size to compare"
                        stack = stack + (tile_image / len(args.images))

                tile_image_to_file(args.out, tile, np.uint8(stack))

            elif args.mode == "list":
                tiles_list.append([tile, fg_ratio, qod])

            progress.update()
            return True, tile

        for tile, ok in executor.map(worker, tiles):
            if not ok and log:
                log.log("Warning: skipping. {}".format(str(tile)))

    if args.mode == "list":
        with open(args.out, mode="w") as out:

            if args.geojson:
                out.write('{"type":"FeatureCollection","features":[')

            first = True
            print("Generate cover in {} with {} tiles, from {}".format(args.out, len(tiles_list), len(tiles)))
            for tile_list in tiles_list:
                tile, fg_ratio, qod = tile_list
                x, y, z = list(map(str, tile))
                if args.geojson:
                    prop = '"properties":{{"x":{},"y":{},"z":{},"fg":{:.1f},"qod":{:.1f}}}'.format(x, y, z, fg_ratio, qod)
                    geom = '"geometry":{}'.format(json.dumps(feature(tile, precision=6)["geometry"]))
                    out.write('{}{{"type":"Feature",{},{}}}'.format("," if not first else "", geom, prop))
                    first = False
                else:
                    out.write("{},{},{}\t{:.1f}\t{:.1f}{}".format(x, y, z, fg_ratio, qod, os.linesep))

            if args.geojson:
                out.write("]}")
            out.close()

    base_url = args.web_ui_base_url if args.web_ui_base_url else "./"

    if args.mode == "side" and not args.no_web_ui:
        template = "compare.html" if not args.web_ui_template else args.web_ui_template
        web_ui(args.out, base_url, tiles, tiles_compare, args.format, template)

    if args.mode == "stack" and not args.no_web_ui:
        template = "leaflet.html" if not args.web_ui_template else args.web_ui_template
        tiles = [tile for tile, _ in tiles_from_slippy_map(args.images[0])]
        web_ui(args.out, base_url, tiles, tiles_compare, args.format, template)

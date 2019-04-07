import os
import sys
import shutil

from glob import glob
from tqdm import tqdm

from robosat_pink.tiles import tiles_from_csv
from robosat_pink.web_ui import web_ui


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser(
        "subset", help="Filter images in a slippy map dir using a csv tiles cover", formatter_class=formatter_class
    )
    inp = parser.add_argument_group("Inputs")
    inp.add_argument("--dir", type=str, required=True, help="to XYZ tiles input dir path [required]")
    inp.add_argument("--cover", type=str, required=True, help="path to csv cover file to filter dir by [required]")

    mode = parser.add_argument_group("Alternate modes, as default is to copy.")
    mode.add_argument("--move", action="store_true", help="move tiles from input to output")
    mode.add_argument("--delete", action="store_true", help="delete tiles listed in cover")

    out = parser.add_argument_group("Output")
    out.add_argument("out", type=str, nargs="?", default=os.getcwd(), help="output dir path [required for copy or move]")

    ui = parser.add_argument_group("Web UI")
    ui.add_argument("--web_ui_base_url", type=str, help="alternate Web UI base URL")
    ui.add_argument("--web_ui_template", type=str, help="alternate Web UI template path")
    ui.add_argument("--no_web_ui", action="store_true", help="desactivate Web UI output")

    parser.set_defaults(func=main)


def main(args):
    if not args.out and not args.delete:
        sys.exit("ERROR: out parameter is required")

    args.out = os.path.expanduser(args.out)
    extension = ""

    print("RoboSat.pink - subset {} with cover {}".format(args.dir, args.cover))

    tiles = set(tiles_from_csv(os.path.expanduser(args.cover)))
    for tile in tqdm(tiles, desc="Subset", unit="tiles", ascii=True):

        paths = glob(os.path.join(os.path.expanduser(args.dir), str(tile.z), str(tile.x), "{}.*".format(tile.y)))
        if len(paths) != 1:
            print("Warning: {} skipped.".format(tile))
            continue
        src = paths[0]

        try:
            if not os.path.isdir(os.path.join(args.out, str(tile.z), str(tile.x))):
                os.makedirs(os.path.join(args.out, str(tile.z), str(tile.x)), exist_ok=True)

            extension = os.path.splitext(src)[1][1:]
            dst = os.path.join(args.out, str(tile.z), str(tile.x), "{}.{}".format(tile.y, extension))

            if args.move:
                assert os.path.isfile(src)
                shutil.move(src, dst)

            elif args.delete:
                assert os.path.isfile(src)
                os.remove(src)

            else:
                shutil.copyfile(src, dst)

        except:
            sys.exit("Error: Unable to process tile: {}".format(str(tile)))

    if not args.no_web_ui and not args.delete:
        template = "leaflet.html" if not args.web_ui_template else args.web_ui_template
        base_url = args.web_ui_base_url if args.web_ui_base_url else "./"
        web_ui(args.out, base_url, tiles, tiles, extension, template)

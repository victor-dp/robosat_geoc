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
    choices = {"copy", "move", "delete"}
    inp.add_argument("--dir", type=str, required=True, help="to XYZ tiles input dir path [required]")
    inp.add_argument("--filter", type=str, required=True, help="path to csv cover file to filter dir by [required]")
    inp.add_argument("--mode", type=str, default="copy", choices=choices, help="subset mode [default: copy]")

    out = parser.add_argument_group("Output")
    out.add_argument("out", type=str, nargs='?', default=os.getcwd(), help="output dir path [required for copy or move]")

    ui = parser.add_argument_group("Web UI")
    ui.add_argument("--web_ui", action="store_true", help="activate Web UI output")
    ui.add_argument("--web_ui_base_url", type=str, help="alternate Web UI base URL")
    ui.add_argument("--web_ui_template", type=str, help="alternate Web UI template path")

    parser.set_defaults(func=main)


def main(args):
    if not args.out and args.mode in ["copy", "move"]:
        sys.exit("ERROR: out parameter is required")

    tiles = set(tiles_from_csv(args.filter))
    extension = ""

    for tile in tqdm(tiles, desc="Subset", unit="tiles", ascii=True):

        paths = glob(os.path.join(args.dir, str(tile.z), str(tile.x), "{}.*".format(tile.y)))
        if len(paths) != 1:
            print("Warning: {} skipped.".format(tile))
            continue
        src = paths[0]

        try:
            if not os.path.isdir(os.path.join(args.out, str(tile.z), str(tile.x))):
                os.makedirs(os.path.join(args.out, str(tile.z), str(tile.x)), exist_ok=True)

            extension = os.path.splitext(src)[1][1:]
            dst = os.path.join(args.out, str(tile.z), str(tile.x), "{}.{}".format(tile.y, extension))

            if args.mode == "move":
                assert os.path.isfile(src)
                shutil.move(src, dst)

            if args.mode == "copy":
                shutil.copyfile(src, dst)

            if args.mode == "delete":
                assert os.path.isfile(src)
                os.remove(src)

        except:
            sys.exit("Error: Unable to process {}".format(tile))

    if args.web_ui:
        template = "leaflet.html" if not args.web_ui_template else args.web_ui_template
        base_url = args.web_ui_base_url if args.web_ui_base_url else "./"
        web_ui(args.out, base_url, tiles, tiles, extension, template)

import os
import sys

from importlib import import_module

import numpy as np

import torch
import torch.backends.cudnn
from torch.utils.data import DataLoader

from tqdm import tqdm
from PIL import Image

from robosat_pink.tiles import tiles_from_slippy_map
from robosat_pink.config import load_config, check_model, check_classes, check_channels
from robosat_pink.colors import make_palette
from robosat_pink.web_ui import web_ui
from robosat_pink.logs import Logs


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser(
        "predict", help="Predict masks, from given inputs and an already trained model", formatter_class=formatter_class
    )

    inp = parser.add_argument_group("Inputs")
    inp.add_argument("tiles", type=str, help="tiles directory path [required]")
    inp.add_argument("--checkpoint", type=str, required=True, help="path to the trained model to use [required]")
    inp.add_argument("--config", type=str, help="path to config file [required]")
    inp.add_argument("--model", type=str, help="if set, override model name from config file")
    inp.add_argument("--ts", type=int, help="if set, override tile size value from config file")
    inp.add_argument("--overlap", type=int, default=64, help="tile pixels overlap [default: 64]")

    out = parser.add_argument_group("Outputs")
    out.add_argument("out", type=str, help="output directory path [required]")

    perf = parser.add_argument_group("Data Loaders")
    perf.add_argument("--workers", type=int, help="number of workers to load images [default: GPU x 2]")
    perf.add_argument("--bs", type=int, help="if set, override batch size value from config file")

    ui = parser.add_argument_group("Web UI")
    ui.add_argument("--web_ui_base_url", type=str, help="alternate Web UI base URL")
    ui.add_argument("--web_ui_template", type=str, help="alternate Web UI template path")
    ui.add_argument("--no_web_ui", action="store_true", help="desactivate Web UI output")

    parser.set_defaults(func=main)


def main(args):
    config = load_config(args.config)
    check_channels(config)
    check_classes(config)
    check_model(config)
    args.workers = torch.cuda.device_count() * 2 if torch.device("cuda") and not args.workers else args.workers
    config["model"]["bs"] = args.bs if args.bs else config["model"]["bs"]
    config["model"]["ts"] = args.ts if args.ts else config["model"]["ts"]
    config["model"]["name"] = args.model if args.model else config["model"]["name"]

    log = Logs(os.path.join(args.out, "log"))

    if torch.cuda.is_available():
        log.log("RoboSat.pink - predict on {} GPUs, with {} workers".format(torch.cuda.device_count(), args.workers))
        log.log("(Torch:{} Cuda:{} CudNN:{})".format(torch.__version__, torch.version.cuda, torch.backends.cudnn.version()))
        device = torch.device("cuda")
        torch.backends.cudnn.benchmark = True
    else:
        log.log("RoboSat.pink - predict on CPU, with {} workers".format(args.workers))
        device = torch.device("cpu")

    def map_location(storage, _):
        return storage.cuda() if torch.cuda.is_available() else storage.cpu()

    try:
        model_module = import_module("robosat_pink.models.{}".format(config["model"]["name"].lower()))
    except:
        sys.exit("ERROR: Unknown {} model.".format(config["model"]["name"]))

    try:
        # FIXME https://github.com/pytorch/pytorch/issues/7178
        chkpt = torch.load(args.checkpoint, map_location=map_location)

        net = getattr(model_module, config["model"]["name"])(config).to(device)
        net = torch.nn.DataParallel(net)
        net.load_state_dict(chkpt["state_dict"])
        net.eval()
    except:
        sys.exit("ERROR: Unable to load {} in {} model.".format(args.checkpoint, config["model"]["name"]))

    loader_module = import_module("robosat_pink.loaders.{}".format(config["model"]["loader"].lower()))
    loader_predict = getattr(loader_module, config["model"]["loader"])(
        config, args.tiles, mode="predict", overlap=args.overlap
    )
    loader = DataLoader(loader_predict, batch_size=config["model"]["bs"], num_workers=args.workers)
    palette = make_palette(config["classes"][0]["color"], config["classes"][1]["color"])

    with torch.no_grad():  # don't track tensors with autograd during prediction

        for images, tiles in tqdm(loader, desc="Eval", unit="batch", ascii=True):

            images = images.to(device)

            try:
                outputs = net(images)
                probs = torch.nn.functional.softmax(outputs, dim=1).data.cpu().numpy()
            except:
                log.log("WARNING: Skipping batch:")
                for tile, prob in zip(tiles, probs):
                    log.log(" - {}".format(str(tile)))
                continue

            for tile, prob in zip(tiles, probs):
                x, y, z = list(map(int, tile))

                try:
                    prob = loader_predict.remove_overlap(prob)  # as we predicted on buffered tiles
                    image = np.around(prob[1:, :, :]).astype(np.uint8).squeeze()

                    os.makedirs(os.path.join(args.out, str(z), str(x)), exist_ok=True)
                    out = Image.fromarray(image, mode="P")
                    out.putpalette(palette)
                    out.save(os.path.join(args.out, str(z), str(x), str(y) + ".png"), optimize=True)
                except:
                    log.log("WARNING: Skipping tile {}".format(str(tile)))

    if not args.no_web_ui:
        template = "leaflet.html" if not args.web_ui_template else args.web_ui_template
        base_url = args.web_ui_base_url if args.web_ui_base_url else "./"
        tiles = [tile for tile, _ in tiles_from_slippy_map(args.out)]
        web_ui(args.out, base_url, tiles, tiles, "png", template)

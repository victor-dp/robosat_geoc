import sys

from importlib import import_module

import torch
import torch.onnx
import torch.autograd

from robosat_pink.config import load_config, check_classes, check_model


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser("export", help="Export a model to ONNX or Torch JIT", formatter_class=formatter_class)

    inp = parser.add_argument_group("Inputs")
    inp.add_argument("--checkpoint", type=str, required=True, help="model checkpoint to load [required]")
    inp.add_argument("--type", type=str, choices=["onnx", "jit"], default="jit", help="output type [default: jit]")
    inp.add_argument("--config", type=str, help="path to config file [required]")
    out = parser.add_argument_group("Output")
    out.add_argument("out", type=str, help="path to save export model to [required]")

    parser.set_defaults(func=main)


def main(args):
    config = load_config(args.config)
    check_classes(config)
    check_model(config)

    # FIXME
    def map_location(storage, _):
        return storage.cpu()

    print("RoboSat.pink - export to {} - (Torch:{})".format(args.type, torch.__version__))

    try:
        model_module = import_module("robosat_pink.models.{}".format(config["model"]["name"].lower()))
    except:
        sys.exit("ERROR: Unknown {} model.".format(config["model"]["name"]))

    try:
        net = getattr(model_module, config["model"]["name"])(config).to("cpu")
        chkpt = torch.load(args.checkpoint, map_location=map_location)
    except:
        sys.exit("ERROR: Unable to load {} in {} model.".format(args.checkpoint, config["model"]["name"]))

    try:  # https://github.com/pytorch/pytorch/issues/9176
        net.module.state_dict(chkpt["state_dict"])
    except AttributeError:
        net.state_dict(chkpt["state_dict"])

    num_channels = 0
    for channel in config["channels"]:
        for band in channel["bands"]:
            num_channels += 1

    batch = torch.rand(1, num_channels, config["model"]["tile_size"], config["model"]["tile_size"])

    try:
        if args.type == "onnx":
            torch.onnx.export(net, torch.autograd.Variable(batch), args.out)

        if args.type == "jit":
            torch.jit.trace(net, batch).save(args.out)
    except:
        sys.exit("ERROR: Unable to export model {} in {}.".format(config["model"]["name"]), args.type)

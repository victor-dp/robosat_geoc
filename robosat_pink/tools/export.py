import sys

from importlib import import_module

import torch
import torch.onnx
import torch.autograd

from robosat_pink.config import load_config


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser("export", help="Export a model to ONNX or Torch JIT", formatter_class=formatter_class)

    inp = parser.add_argument_group("Inputs")
    inp.add_argument("--checkpoint", type=str, required=True, help="model checkpoint to load [required]")
    inp.add_argument("--config", type=str, required=True, help="path to configuration file [required]")
    inp.add_argument("--type", type=str, choices=["onnx", "jit"], default="jit", help="output type [default: jit]")
    out = parser.add_argument_group("Output")
    out.add_argument("out", type=str, help="path to save export model to [required]")

    parser.set_defaults(func=main)


def main(args):
    config = load_config(args.config)

    def map_location(storage, _):
        return storage.cpu()

    try:
        model_module = import_module("robosat_pink.models.{}".format(config["model"]["name"]))
    except:
        sys.exit("Unknown {} model".format(config["model"]["name"]))

    net = getattr(model_module, "{}".format(config["model"]["name"].title()))(config).to("cpu")
    chkpt = torch.load(args.checkpoint, map_location=map_location)

    try:  # https://github.com/pytorch/pytorch/issues/9176
        net.module.state_dict(chkpt["state_dict"])
    except AttributeError:
        net.state_dict(chkpt["state_dict"])

    num_channels = 0
    for channel in config["channels"]:
        for band in channel["bands"]:
            num_channels += 1

    batch = torch.rand(1, num_channels, config["model"]["tile_size"], config["model"]["tile_size"])

    if args.type == "onnx":
        torch.onnx.export(net, torch.autograd.Variable(batch), args.out)

    elif args.type == "jit":
        torch.jit.trace(net, batch).save(args.out)

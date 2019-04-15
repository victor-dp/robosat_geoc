import sys

import torch
import torch.onnx
import torch.autograd

from robosat_pink.core import load_module


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser("export", help="Export a model to ONNX or Torch JIT", formatter_class=formatter_class)

    inp = parser.add_argument_group("Inputs")
    inp.add_argument("--checkpoint", type=str, required=True, help="model checkpoint to load [required]")
    inp.add_argument("--type", type=str, choices=["onnx", "jit"], default="jit", help="output type [default: jit]")
    out = parser.add_argument_group("Output")
    out.add_argument("out", type=str, help="path to save export model to [required]")

    parser.set_defaults(func=main)


def main(args):

    try:
        chkpt = torch.load(args.checkpoint, map_location=torch.device("cpu"))
        assert chkpt["producer_name"] == "RoboSat.pink"
    except:
        sys.exit("ERROR: Unable to load checkpoint: {}".format(args.checkpoint))

    model_module = load_module("robosat_pink.models.{}".format(chkpt["nn"].lower()))
    nn = getattr(model_module, chkpt["nn"])(chkpt["shape_in"], chkpt["shape_out"]).to("cpu")

    print("RoboSat.pink - export model to {}".format(args.type))
    print("Model: {} - UUID: {} - Torch {}".format(chkpt["nn"], chkpt["uuid"], torch.__version__))
    print(chkpt["doc_string"])

    try:  # https://github.com/pytorch/pytorch/issues/9176
        nn.module.state_dict(chkpt["state_dict"])
    except AttributeError:
        nn.state_dict(chkpt["state_dict"])

    try:
        batch = torch.rand(1, *chkpt["shape_in"])
        if args.type == "onnx":
            torch.onnx.export(nn, torch.autograd.Variable(batch), args.out)

        if args.type == "jit":
            torch.jit.trace(nn, batch).save(args.out)
    except:
        sys.exit("ERROR: Unable to export model {} in {}.".format(chkpt["uuid"]), args.type)

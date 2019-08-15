import os
import sys
import torch
from os import path


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser("info", help="Provide informations", formatter_class=formatter_class)
    parser.set_defaults(func=main)


def main(args):

    print("========================================")
    print("RoboSat.pink " + open(path.join(path.dirname(__file__), "../../VERSION")).read())
    print("Python:  " + sys.version[:5])
    print("Torch:   " + torch.__version__)
    print("CPUs:    " + str(os.cpu_count()))
    print("GPUs:    " + str(torch.cuda.device_count()))
    print("Cuda:    " + torch.version.cuda)
    print("Cudnn:   " + str(torch.backends.cudnn.version()))
    print("========================================")
    print(torch.__config__.parallel_info())
    print("========================================")

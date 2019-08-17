import os
import sys
import cv2
import torch
import rasterio
import robosat_pink as rsp
from os import path


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser("info", help="Provide informations", formatter_class=formatter_class)
    parser.set_defaults(func=main)


def main(args):

    print("========================================")
    print("RoboSat.pink: " + rsp.__version__)
    print("========================================")
    print("Python:  " + sys.version[:5])
    print("Torch:   " + torch.__version__)
    print("OpenCV   " + cv2.__version__)
    print("GDAL     " + rasterio._base.gdal_version())
    print("========================================")
    print("GPUs:    " + str(torch.cuda.device_count()))
    print("Cuda:    " + torch.version.cuda)
    print("Cudnn:   " + str(torch.backends.cudnn.version()))
    print("========================================")
    print("CPUs:    " + str(os.cpu_count()))
    print(torch.__config__.parallel_info())
    print("========================================")

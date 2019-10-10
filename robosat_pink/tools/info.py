import os
import re
import sys
import cv2
import torch
import rasterio
import robosat_pink as rsp


def add_parser(subparser, formatter_class):
    epilog = "Usages:\nTo kill GPU processes: rsp info --processes | xargs sudo kill -9"
    parser = subparser.add_parser("info", help="Provide informations", formatter_class=formatter_class, epilog=epilog)
    parser.add_argument("--processes", action="store_true", help="if set, output GPU processes list")
    parser.set_defaults(func=main)


def main(args):

    if args.processes:
        devices = os.getenv("CUDA_VISIBLE_DEVICES")
        assert devices, "CUDA_VISIBLE_DEVICES not set."
        pids = set()
        for i in devices.split(","):
            lsof = os.popen("lsof /dev/nvidia{}".format(i)).read()
            for row in re.sub("( )+", "|", lsof).split("\n"):
                try:
                    pid = row.split("|")[1]
                    pids.add(int(pid))
                except:
                    continue

        for pid in sorted(pids):
            print("{} ".format(pid), end="")

        sys.exit()

    print("========================================")
    print("RoboSat.pink: " + rsp.__version__)
    print("========================================")
    print("Python  " + sys.version[:5])
    print("Torch   " + torch.__version__)
    print("OpenCV  " + cv2.__version__)
    print("GDAL    " + rasterio._base.gdal_version())
    print("Cuda    " + torch.version.cuda)
    print("Cudnn   " + str(torch.backends.cudnn.version()))
    print("========================================")
    print("CPUs    " + str(os.cpu_count()))
    print("GPUs    " + str(torch.cuda.device_count()))
    for i in range(torch.cuda.device_count()):
        print(" - " + torch.cuda.get_device_name(i))
    print("========================================")

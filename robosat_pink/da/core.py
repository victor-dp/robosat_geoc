"""PyTorch-compatible Data Augmentation."""

import sys
import torch
import numpy as np
from importlib import import_module


def to_normalized_tensor(config, mode, image, mask=None):

    assert mode == "train" or mode == "predict"

    # To Tensor and Data Augmentation
    if mode == "train":
        try:
            module = import_module("robosat_pink.da.{}".format(config["model"]["da"].lower()))
        except:
            sys.exit("Unable to load data augmentation module")

        transform = module.transform(config, image, mask)
        image = torch.from_numpy(np.moveaxis(transform["image"], 2, 0)).float()
        mask = torch.from_numpy(transform["mask"]).long()

    elif mode == "predict":
        image = torch.from_numpy(np.moveaxis(image, 2, 0)).float()

    # Normalize
    std = []
    mean = []

    try:
        for channel in config["channels"]:
            std.extend(channel["std"])
            mean.extend(channel["mean"])
    except:
        if config["model"]["pretrained"] and not len(std) and not len(mean):
            mean = [0.485, 0.456, 0.406]  # Use RGB ImageNet default
            std = [0.229, 0.224, 0.225]  # Use RGB ImageNet default

    assert len(std) and len(mean)
    image.sub_(torch.as_tensor(mean, device=image.device)[:, None, None])
    image.div_(torch.as_tensor(std, device=image.device)[:, None, None])

    if mode == "train":
        assert image is not None and mask is not None
        return image, mask

    elif mode == "predict":
        assert image is not None
        return image

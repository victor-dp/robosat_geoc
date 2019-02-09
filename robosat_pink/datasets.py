"""PyTorch-compatible datasets.

Guaranteed to implement `__len__`, and `__getitem__`.

See: https://pytorch.org/docs/stable/data.html
"""

import os
import sys

import numpy as np
from PIL import Image

import torch
import torch.utils.data

from robosat_pink.tiles import tiles_from_slippy_map, tile_image_buffer, tile_image


class SlippyMapTiles(torch.utils.data.Dataset):
    """Dataset for images stored in slippy map format. """

    def __init__(self, root, mode, transform=None):
        super().__init__()

        self.tiles = []
        self.transform = transform

        self.tiles = [(tile, path) for tile, path in tiles_from_slippy_map(root)]
        self.tiles.sort(key=lambda tile: tile[0])
        self.mode = mode

    def __len__(self):
        return len(self.tiles)

    def __getitem__(self, i):
        tile, path = self.tiles[i]

        if self.mode == "mask":
            image = np.array(Image.open(path).convert("P"))

        elif self.mode == "image":
            image = tile_image(path)

        if self.transform is not None:
            image = self.transform(image)

        return image, tile


class SlippyMapTilesConcatenation(torch.utils.data.Dataset):
    """Dataset to concate multiple input images stored in slippy map format. """

    def __init__(self, path, channels, target, joint_transform=None):
        super().__init__()

        assert len(channels), "Channels configuration empty"
        self.channels = channels
        self.inputs = dict()

        for channel in channels:
            for band in channel["bands"]:
                self.inputs[channel["sub"]] = SlippyMapTiles(os.path.join(path, channel["sub"]), mode="image")

        self.target = SlippyMapTiles(target, mode="mask")

        # No transformations in the `SlippyMapTiles` instead joint transformations in getitem
        self.joint_transform = joint_transform

    def __len__(self):
        return len(self.target)

    def __getitem__(self, i):

        mask, tile = self.target[i]

        for channel in self.channels:
            try:
                data, band_tile = self.inputs[channel["sub"]][i]
                assert band_tile == tile

                for band in channel["bands"]:
                    data_band = data[:, :, int(band) - 1] if len(data.shape) == 3 else []
                    data_band = data_band.reshape(mask.shape[0], mask.shape[1], 1)
                    tensor = np.concatenate((tensor, data_band), axis=2) if "tensor" in locals() else data_band  # noqa F821
            except:
                sys.exit("Unable to concatenate input Tensor")

        if self.joint_transform is not None:
            tensor, mask = self.joint_transform(tensor, mask)

        return tensor, mask, tile


class BufferedSlippyMapTiles(torch.utils.data.Dataset):
    """Dataset for buffered slippy map tiles with overlap.

       Note: The overlap must not span multiple tiles.
             Use `unbuffer` to get back the original tile.
    """

    def __init__(self, root, transform=None, size=512, overlap=32):

        super().__init__()

        assert overlap >= 0
        assert size >= 256

        self.transform = transform
        self.size = size
        self.overlap = overlap
        self.tiles = list(tiles_from_slippy_map(root))

    def __len__(self):
        return len(self.tiles)

    def __getitem__(self, i):
        tile, path = self.tiles[i]
        image = np.array(tile_image_buffer(tile, self.tiles, overlap=self.overlap, tile_size=self.size))

        if self.transform is not None:
            image = self.transform(image)

        return image, torch.IntTensor([tile.x, tile.y, tile.z])

    def unbuffer(self, probs):
        o = self.overlap
        _, x, y = probs.shape

        return probs[:, o : x - o, o : y - o]

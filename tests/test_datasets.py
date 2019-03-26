import unittest

import torch
import mercantile

from robosat_pink.datasets import DatasetTilesSemSeg
from robosat_pink.transforms import ImageToTensor, JointTransform


class TestDatasetSemSeg(unittest.TestCase):
    def test_len(self):
        path = "tests/fixtures"
        config = {"channels": [{"name": "images", "bands": [1, 2, 3]}]}
        transform = ImageToTensor()

        # mode train
        dataset = DatasetTilesSemSeg(config, path, transform, "train")
        self.assertEqual(len(dataset), 3)

        # mode predict
        dataset = DatasetTilesSemSeg(config, path, transform, "predict", 64)
        self.assertEqual(len(dataset), 3)

    def test_getitem(self):
        path = "tests/fixtures"
        config = {"channels": [{"name": "images", "bands": [1, 2, 3]}]}

        # mode train
        transform = JointTransform(None, None)
        dataset = DatasetTilesSemSeg(config, path, transform, "train")
        image, mask, tile = dataset[0]

        assert tile == mercantile.Tile(69105, 105093, 18)
        self.assertEqual(image.size, 512 * 512 * 3)
        self.assertEqual(image.shape, (512, 512, 3))

        # mode predict
        transform = ImageToTensor()
        dataset = DatasetTilesSemSeg(config, path, transform, "predict", 64)
        images, tiles = dataset[0]

        self.assertEqual(type(images), torch.Tensor)
        x, y, z = tiles.numpy()
        self.assertEqual(mercantile.Tile(x, y, z), mercantile.Tile(69105, 105093, 18))

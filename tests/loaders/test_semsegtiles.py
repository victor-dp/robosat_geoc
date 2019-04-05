import unittest

import torch
import mercantile

from robosat_pink.loaders.semsegtiles import SemSegTiles


class TestSemSegTiles(unittest.TestCase):
    def test_len(self):
        path = "tests/fixtures"
        config = {
            "channels": [{"name": "images", "bands": [1, 2, 3]}],
            "model": {"pretrained": True, "da": "Strong", "ts": 512},
        }

        # mode train
        dataset = SemSegTiles(config, path, "train")
        self.assertEqual(len(dataset), 3)

        # mode predict
        dataset = SemSegTiles(config, path, "predict")
        self.assertEqual(len(dataset), 3)

    def test_getitem(self):
        path = "tests/fixtures"
        config = {
            "channels": [{"name": "images", "bands": [1, 2, 3]}],
            "model": {"pretrained": True, "da": "Strong", "ts": 512},
        }

        # mode train
        dataset = SemSegTiles(config, path, "train")
        image, mask, tile = dataset[0]

        assert tile == mercantile.Tile(69105, 105093, 18)
        self.assertEqual(image.shape, torch.Size([3, 512, 512]))

        # mode predict
        dataset = SemSegTiles(config, path, "predict")
        images, tiles = dataset[0]

        self.assertEqual(type(images), torch.Tensor)
        x, y, z = tiles.numpy()
        self.assertEqual(mercantile.Tile(x, y, z), mercantile.Tile(69105, 105093, 18))

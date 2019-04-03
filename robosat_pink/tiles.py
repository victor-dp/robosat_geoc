"""Slippy Map Tiles.
   See: https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
"""

import io
import os
import re
import glob
import warnings

import numpy as np
from PIL import Image
from rasterio import open as rasterio_open
import cv2

import csv
import mercantile

warnings.simplefilter("ignore", UserWarning)  # To prevent rasterio NotGeoreferencedWarning


def tile_pixel_to_location(tile, dx, dy):
    """Converts a pixel in a tile to lon/lat coordinates."""

    assert 0 <= dx <= 1 and 0 <= dy <= 1, "x and y offsets must be in [0, 1]"

    w, s, e, n = mercantile.bounds(tile)

    def lerp(a, b, c):
        return a + c * (b - a)

    return lerp(w, e, dx), lerp(s, n, dy)  # lon, lat


def tiles_from_slippy_map(root):
    """Loads files from an on-disk slippy map dir."""

    root = os.path.expanduser(root)
    paths = glob.glob(os.path.join(root, "[0-9]*/[0-9]*/[0-9]*.*"))

    for path in paths:
        tile = re.match(os.path.join(root, "(?P<z>[0-9]+)/(?P<x>[0-9]+)/(?P<y>[0-9]+).+"), path)
        if not tile:
            continue

        yield mercantile.Tile(int(tile["x"]), int(tile["y"]), int(tile["z"])), path


def tile_from_slippy_map(root, x, y, z):
    """Retrieve a single tile from a slippy map dir."""

    path = glob.glob(os.path.join(os.path.expanduser(root), str(z), str(x), str(y) + ".*"))
    if not path:
        return None

    return mercantile.Tile(x, y, z), path[0]


def tiles_from_csv(path):
    """Retrieve tiles from a line-delimited csv file."""

    with open(os.path.expanduser(path)) as fp:
        reader = csv.reader(fp)

        for row in reader:
            if not row:
                continue

            yield mercantile.Tile(*map(int, row))


def tile_image_from_file(path, bands=None):
    """Return a multiband image numpy array, from an image file path, or None."""

    try:
        if path[-3:] == "png":
            return np.array(Image.open(os.path.expanduser(path)).convert("RGB"))

        raster = rasterio_open(os.path.expanduser(path))
    except:
        return None

    image = None
    for i in raster.indexes if bands is None else bands:
        data_band = raster.read(i)
        data_band = data_band.reshape(data_band.shape[0], data_band.shape[1], 1)  # H,W -> H,W,C
        image = np.concatenate((image, data_band), axis=2) if image is not None else data_band

    return image


def tile_image_to_file(root, tile, image):
    """ Write an image tile on disk. """

    out_path = os.path.join(os.path.expanduser(root), str(tile.z), str(tile.x))
    os.makedirs(out_path, exist_ok=True)

    if image.shape[2] > 3:
        ext = "tiff"
    else:
        ext = "webp"

    return cv2.imwrite(os.path.join(out_path, "{}.{}").format(str(tile.y), ext), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))


def tile_label_from_file(path):
    """Return a numpy array, from a label file path, or None."""

    try:
        return np.array(Image.open(os.path.expanduser(path)))
    except:
        return None


def tile_label_to_file(root, tile, palette, label):
    """ Write a label tile on disk. """

    out_path = os.path.join(os.path.expanduser(root), str(tile.z), str(tile.x))
    os.makedirs(out_path, exist_ok=True)

    if len(label.shape) == 3:  # H,W,C -> H,W
        assert label.shape[2] == 1
        label = label.reshape((label.shape[0], label.shape[1]))

    out = Image.fromarray(label, mode="P")
    out.putpalette(palette)

    try:
        out.save(os.path.join(out_path, "{}.png".format(str(tile.y))), optimize=True)
        return True
    except:
        return False


def tile_image_from_url(requests_session, url, timeout=10):
    """Fetch a tile image using HTTP, and return it or None """

    try:
        resp = requests_session.get(url, timeout=timeout)
        resp.raise_for_status()
        image = np.fromstring(io.BytesIO(resp.content).read(), np.uint8)
        return cv2.cvtColor(cv2.imdecode(image, cv2.IMREAD_ANYCOLOR), cv2.COLOR_BGR2RGB)

    except Exception:
        return None


def tile_image_buffer(tile, path, overlap=64, bands=None):
    """Buffers a tile image adding borders on all sides based on adjacent tiles, if presents, or with zeros."""

    def tile_image_adjacent(root, tile, dx, dy, bands):
        tile = tile_from_slippy_map(root, int(tile.x) + dx, int(tile.y) + dy, int(tile.z))
        return None if not tile else tile_image_from_file(tile[1], bands)

    root = re.sub("^(.+)(/[0-9]+/[0-9]+/[0-9]+.+)$", r"\1", path)

    # 3x3 matrix (upper, center, bottom) x (left, center, right)
    ul = tile_image_adjacent(root, tile, -1, -1, bands)
    uc = tile_image_adjacent(root, tile, +0, -1, bands)
    ur = tile_image_adjacent(root, tile, +1, -1, bands)
    cl = tile_image_adjacent(root, tile, -1, +0, bands)
    cc = tile_image_adjacent(root, tile, +0, +0, bands)
    cr = tile_image_adjacent(root, tile, +1, +0, bands)
    bl = tile_image_adjacent(root, tile, -1, +1, bands)
    bc = tile_image_adjacent(root, tile, +0, +1, bands)
    br = tile_image_adjacent(root, tile, +1, +1, bands)

    assert cc is not None, "Unable to retrieve image to buffer"
    o = overlap
    oo = overlap * 2
    ts = cc.shape[1]
    assert 0 <= overlap <= ts, "Overlap value can't be either negative or bigger than tile size"

    img = np.zeros((ts + oo, ts + oo, 3)).astype(np.uint8)

    # fmt:off
    img[0:o,        0:o,        :] = ul[-o:ts, -o:ts, :] if ul is not None else np.zeros((o,   o, 3)).astype(np.uint8)
    img[0:o,        o:ts+o,     :] = uc[-o:ts,  0:ts, :] if uc is not None else np.zeros((o,  ts, 3)).astype(np.uint8)
    img[0:o,        ts+o:ts+oo, :] = ur[-o:ts,   0:o, :] if ur is not None else np.zeros((o,   o, 3)).astype(np.uint8)
    img[o:ts+o,     0:o,        :] = cl[0:ts,  -o:ts, :] if cl is not None else np.zeros((ts,  o, 3)).astype(np.uint8)
    img[o:ts+o,     o:ts+o,     :] = cc                  if cc is not None else np.zeros((ts, ts, 3)).astype(np.uint8)
    img[o:ts+o,     ts+o:ts+oo, :] = cr[0:ts,    0:o, :] if cr is not None else np.zeros((ts,  o, 3)).astype(np.uint8)
    img[ts+o:ts+oo, 0:o,        :] = bl[0:o,   -o:ts, :] if bl is not None else np.zeros((o,   o, 3)).astype(np.uint8)
    img[ts+o:ts+oo, o:ts+o,     :] = bc[0:o,    0:ts, :] if bc is not None else np.zeros((o,  ts, 3)).astype(np.uint8)
    img[ts+o:ts+oo, ts+o:ts+oo, :] = br[0:o,     0:o, :] if br is not None else np.zeros((o,   o, 3)).astype(np.uint8)
    # fmt:on

    return img

"""Slippy Map Tiles.
   See: https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
"""

import io
import os
import re
import glob

import cv2
import numpy as np

import csv
import mercantile


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

    path = glob.glob(os.path.join(os.path.expanduser(root), z, x, y + ".*"))
    if not path:
        return None

    return mercantile.Tile(x, y, z), path[0]


def tiles_from_csv(path):
    """Retrieve tiles from a line-delimited csv file."""

    path = os.path.expanduser(path)
    with open(path) as fp:
        reader = csv.reader(fp)

        for row in reader:
            if not row:
                continue

            yield mercantile.Tile(*map(int, row))


def tile_image_from_file(path):
    """Return a multiband image numpy array, from a file path."""

    path = os.path.expanduser(path)
    image = cv2.imread(path, cv2.IMREAD_ANYCOLOR)
    if len(image.shape) == 3 and image.shape[2] >= 3:  # multibands BGR2RGB
        b = image[:, :, 0]
        image[:, :, 0] = image[:, :, 2]
        image[:, :, 2] = b

    return image


def tile_image_from_url(session, url, timeout=10):
    """Fetch a tile image using HTTP. Need requests.Session."""

    try:
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
        return io.BytesIO(resp.content)

    except Exception:
        return None


def tile_image_adjacent(tile, dx, dy, tiles):
    """Retrieves an adjacent tile image if exists from a tile store, or None."""

    try:
        path = tiles[mercantile.Tile(x=int(tile.x) + dx, y=int(tile.y) + dy, z=int(tile.z))]
    except KeyError:
        return None

    return tile_image_from_file(path)


def tile_image_buffer(tile, tiles, overlap, tile_size):
    """Buffers a tile image adding borders on all sides based on adjacent tiles."""

    assert 0 <= overlap <= tile_size, "Overlap value can't be either negative or bigger than tile_size"

    tiles = dict(tiles)
    x, y, z = map(int, [tile.x, tile.y, tile.z])

    # 3x3 matrix (upper, center, bottom) x (left, center, right)
    ul = tile_image_adjacent(tile, -1, -1, tiles)
    uc = tile_image_adjacent(tile, +0, -1, tiles)
    ur = tile_image_adjacent(tile, +1, -1, tiles)
    cl = tile_image_adjacent(tile, -1, +0, tiles)
    cc = tile_image_adjacent(tile, +0, +0, tiles)
    cr = tile_image_adjacent(tile, +1, +0, tiles)
    bl = tile_image_adjacent(tile, -1, +1, tiles)
    bc = tile_image_adjacent(tile, +0, +1, tiles)
    br = tile_image_adjacent(tile, +1, +1, tiles)

    ts = tile_size
    o = overlap
    oo = overlap * 2

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

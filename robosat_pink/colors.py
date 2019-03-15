"""Color handling, color maps, color palettes."""

import re
import colorsys
import webcolors


def make_palette(*colors):
    """Builds a PIL color palette from CSS3 color names, or hex values patterns as #RRGGBB."""

    assert 0 < len(colors) <= 256

    hex_colors = [webcolors.CSS3_NAMES_TO_HEX[color] if color[0] != "#" else color for color in colors]
    rgb_colors = [(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)) for h in hex_colors]

    return list(sum(rgb_colors, ()))


def complementary_palette(palette):
    """Creates a PIL complementary colors palette based on an initial PIL palette."""

    comp_palette = []
    colors = [palette[i : i + 3] for i in range(0, len(palette), 3)]

    for color in colors:
        r, g, b = [v for v in color]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        comp_palette.extend(map(int, colorsys.hsv_to_rgb((h + 0.5) % 1, s, v)))

    return comp_palette


def check_color(color):
    """Check if an input color is or not valid (i.e CSS3 color name or #RRGGBB)."""

    hex_color = webcolors.CSS3_NAMES_TO_HEX[color] if color[0] != "#" else color
    return bool(re.match(r"^#([0-9a-fA-F]){6}$", hex_color))

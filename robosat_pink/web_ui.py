import re
import os
import sys
from pathlib import Path
from robosat_pink.tiles import tile_pixel_to_location, tiles_to_geojson


def web_ui(out, base_url, coverage_tiles, selected_tiles, ext, template):

    try:
        if os.path.isfile(os.path.expanduser(template)):
            web_ui = open(os.path.expanduser(template), "r").read()
        else:
            web_ui = open(os.path.join(Path(__file__).parent, "templates", template), "r").read()
    except:
        sys.exit("Unable to open Web UI template {}".format(template))

    web_ui = re.sub("{{base_url}}", base_url, web_ui)
    web_ui = re.sub("{{ext}}", ext, web_ui)
    web_ui = re.sub("{{tiles}}", "tiles.json" if selected_tiles else "''", web_ui)

    if coverage_tiles:
        # Could surely be improve, but for now, took the first tile to center on
        tile = list(coverage_tiles)[0]
        x, y, z = map(int, [tile.x, tile.y, tile.z])
        web_ui = re.sub("{{zoom}}", str(z), web_ui)
        web_ui = re.sub("{{center}}", str(list(tile_pixel_to_location(tile, 0.5, 0.5))[::-1]), web_ui)

    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as fp:
        fp.write(web_ui)

    if selected_tiles:
        with open(os.path.join(out, "tiles.json"), "w", encoding="utf-8") as fp:
            fp.write(tiles_to_geojson(selected_tiles))

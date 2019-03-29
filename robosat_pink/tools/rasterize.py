import io
import os
import sys
import glob
import json
import struct
import collections

import numpy as np
from tqdm import tqdm

import mercantile
from rasterio.crs import CRS
from rasterio.transform import from_bounds
from rasterio.features import rasterize
from rasterio.warp import transform
from supermercado import burntiles

from robosat_pink.config import load_config, check_classes
from robosat_pink.tiles import tiles_from_csv, tile_label_to_file
from robosat_pink.web_ui import web_ui
from robosat_pink.logs import Logs

import psycopg2


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser(
        "rasterize", help="Rasterize GeoJSON or PostGIS features to tiles", formatter_class=formatter_class
    )

    inp = parser.add_argument_group("Inputs [either --postgis or --geojson is required]")
    inp.add_argument("cover", type=str, help="path to csv tiles cover file [required]")
    inp.add_argument("--postgis", type=str, help="SELECT query to retrieve geometry features [e.g SELECT geom FROM table]")
    inp.add_argument("--geojson", type=str, help="path to GeoJSON features files [e.g /foo/bar/*.json] ")
    inp.add_argument("--config", type=str, help="path to config file [required]")

    out = parser.add_argument_group("Outputs")
    out.add_argument("out", type=str, help="output directory path [required]")
    out.add_argument("--tile_size", type=int, default=512, help="output tile size [default: 512]")

    ui = parser.add_argument_group("Web UI")
    ui.add_argument("--web_ui_base_url", type=str, help="alternate Web UI base URL")
    ui.add_argument("--web_ui_template", type=str, help="alternate Web UI template path")
    ui.add_argument("--no_web_ui", action="store_true", help="desactivate Web UI output")

    parser.set_defaults(func=main)


def geojson_reproject(feature, srid_in, srid_out):
    """Reproject GeoJSON Polygon feature coords
       Inspired by: https://gist.github.com/dnomadb/5cbc116aacc352c7126e779c29ab7abe
    """

    if feature["geometry"]["type"] == "Polygon":
        xys = (zip(*ring) for ring in feature["geometry"]["coordinates"])
        xys = (list(zip(*transform(CRS.from_epsg(srid_in), CRS.from_epsg(srid_out), *xy))) for xy in xys)

        yield {"coordinates": list(xys), "type": "Polygon"}


def geojson_tile_burn(tile, features, srid, tile_size, burn_value=1):
    """Burn tile with GeoJSON features."""

    shapes = ((geometry, burn_value) for feature in features for geometry in geojson_reproject(feature, srid, 3857))

    bounds = mercantile.xy_bounds(tile)
    transform = from_bounds(*bounds, tile_size, tile_size)

    return rasterize(shapes, out_shape=(tile_size, tile_size), transform=transform)


def wkb_to_numpy(wkb):
    """Convert a PostGIS WKB raster to a NumPy array.
       Inspired by: https://github.com/nathancahill/wkb-raster

       PostGIS WKB RFC: http://trac.osgeo.org/postgis/browser/trunk/raster/doc/RFC2-WellKnownBinaryFormat
    """

    out = None

    if not wkb:
        return None

    endian = ">" if struct.unpack("<b", wkb.read(1)) == 0 else "<"  # raster Endiannes
    (_, bands, _, _, _, _, _, _, srid, width, height) = struct.unpack(endian + "HHddddddIHH", wkb.read(60))  # MetaData

    for band in range(bands):

        bits = int(struct.unpack(endian + "b", wkb.read(1))[0])  # header band attributes
        if bool(bits & 128):
            sys.exit("OffLine PostGIS WKB Data not supported.")

        size = [1, 1, 1, 1, 1, 2, 2, 4, 4, 4, 8][bits & 15]
        dtype = ["b1", "u1", "u1", "i1", "u1", "i2", "u2", "i4", "u4", "f4", "f8"][bits & 15]

        wkb.read(size)  # Skip raster NoData value

        if band == 0:
            out = np.zeros((height, width, bands), dtype=np.dtype(dtype))
            pixtype = bits & 15
        elif pixtype != bits & 15:
            sys.exit("Mixed PostGIS WBK Data type not supported.")

        out[:, :, band] = np.ndarray((height, width), buffer=wkb.read(width * height * size), dtype=np.dtype(dtype))

    return out


def main(args):

    if (args.geojson and args.postgis) or (not args.geojson and not args.postgis):
        sys.exit("ERROR: Input features to rasterize must be either GeoJSON or PostGIS")

    config = load_config(args.config)
    check_classes(config)
    colors = [classe["color"] for classe in config["classes"]]
    burn_value = 1

    args.out = os.path.expanduser(args.out)
    os.makedirs(args.out, exist_ok=True)
    log = Logs(os.path.join(args.out, "log"), out=sys.stderr)

    def geojson_parse_polygon(zoom, srid, feature_map, polygon, i):

        try:
            if srid != 4326:
                polygon = [xy for xy in geojson_reproject({"type": "feature", "geometry": polygon}, srid, 4326)][0]

            for i, ring in enumerate(polygon["coordinates"]):  # GeoJSON coordinates could be N dimensionals
                polygon["coordinates"][i] = [[x, y] for point in ring for x, y in zip([point[0]], [point[1]])]

            for tile in burntiles.burn([{"type": "feature", "geometry": polygon}], zoom=zoom):
                feature_map[mercantile.Tile(*tile)].append({"type": "feature", "geometry": polygon})

        except ValueError:
            log.log("Warning: invalid feature {}, skipping".format(i))

        return feature_map

    def geojson_parse_geometry(zoom, srid, feature_map, geometry, i):

        if geometry["type"] == "Polygon":
            feature_map = geojson_parse_polygon(zoom, srid, feature_map, geometry, i)

        elif geometry["type"] == "MultiPolygon":
            for polygon in geometry["coordinates"]:
                feature_map = geojson_parse_polygon(zoom, srid, feature_map, {"type": "Polygon", "coordinates": polygon}, i)
        else:
            log.log("Notice: {} is a non surfacic geometry type, skipping feature {}".format(geometry["type"], i))

        return feature_map

    if args.geojson:

        try:
            tiles = [tile for tile in tiles_from_csv(os.path.expanduser(args.cover))]
            zoom = tiles[0].z
            assert not [tile for tile in tiles if tile.z != zoom]
        except:
            sys.exit("ERROR: Inconsistent cover {}".format(args.cover))

        feature_map = collections.defaultdict(list)

        log.log("RoboSat.pink - rasterize - Compute spatial index")
        for geojson_file in glob.glob(os.path.expanduser(args.geojson)):

            with open(geojson_file) as geojson:
                try:
                    feature_collection = json.load(geojson)
                except:
                    sys.exit("ERROR: {} is not a valid JSON file.".format(geojson_file))

                try:
                    crs_mapping = {"CRS84": "4326", "900913": "3857"}
                    srid = feature_collection["crs"]["properties"]["name"].split(":")[-1]
                    srid = int(srid) if srid not in crs_mapping else int(crs_mapping[srid])
                except:
                    srid = int(4326)

                for i, feature in enumerate(tqdm(feature_collection["features"], ascii=True, unit="feature")):

                    try:
                        if feature["geometry"]["type"] == "GeometryCollection":
                            for geometry in feature["geometry"]["geometries"]:
                                feature_map = geojson_parse_geometry(zoom, srid, feature_map, geometry, i)
                        else:
                            feature_map = geojson_parse_geometry(zoom, srid, feature_map, feature["geometry"], i)
                    except:
                        sys.exit("ERROR: Unable to parse {}. seems not a valid GEOJSON file.".format(geojson_file))

        log.log("RoboSat.pink - rasterize - rasterizing tiles from {} on cover {}".format(args.geojson, args.cover))
        with open(os.path.join(os.path.expanduser(args.out), "instances.cover"), mode="w") as cover:
            for tile in tqdm(list(tiles_from_csv(os.path.expanduser(args.cover))), ascii=True, unit="tile"):

                try:
                    if tile in feature_map:
                        cover.write("{},{},{}  {}{}".format(tile.x, tile.y, tile.z, len(feature_map[tile]), os.linesep))
                        out = geojson_tile_burn(tile, feature_map[tile], 4326, args.tile_size, burn_value)
                    else:
                        cover.write("{},{},{}  {}{}".format(tile.x, tile.y, tile.z, 0, os.linesep))
                        out = np.zeros(shape=(args.tile_size, args.tile_size), dtype=np.uint8)

                    tile_label_to_file(args.out, tile, colors, out)
                except:
                    log.log("Warning: Unable to rasterize tile. Skipping {}".format(str(tile)))

    if args.postgis:

        try:
            pg_conn = psycopg2.connect(config["dataset"]["pg_dsn"])
            pg = pg_conn.cursor()
        except Exception:
            sys.exit("Unable to connect PostgreSQL: {}".format(config["dataset"]["pg_dsn"]))

        log.log("RoboSat.pink - rasterize - rasterizing tiles from PostGIS on cover {}".format(args.cover))
        log.log(" SQL {}".format(args.postgis))
        try:
            pg.execute("SELECT ST_Srid(geom) AS srid FROM ({} LIMIT 1) AS sub".format(args.postgis))
            srid = pg.fetchone()[0]
        except Exception:
            sys.exit("Unable to retrieve geometry SRID.")

        for tile in tqdm(list(tiles_from_csv(args.cover)), ascii=True, unit="tile"):

            s, w, e, n = mercantile.bounds(tile)
            raster = np.zeros((args.tile_size, args.tile_size))
            tile_size = args.tile_size

            query = """
WITH
     bbox      AS (SELECT ST_Transform(ST_MakeEnvelope({},{},{},{}, 4326), {}  ) AS bbox),
     bbox_merc AS (SELECT ST_Transform(ST_MakeEnvelope({},{},{},{}, 4326), 3857) AS bbox),

     rast_a    AS (SELECT ST_AddBand(
                           ST_SetSRID(
                             ST_MakeEmptyRaster({}, {}, ST_Xmin(bbox), ST_Ymax(bbox), (ST_YMax(bbox) - ST_YMin(bbox)) / {}),
                           3857),
                          '8BUI'::text, 0) AS rast
                   FROM bbox_merc),

     features  AS (SELECT ST_Union(ST_Transform(ST_Force2D(geom), 3857)) AS geom
                   FROM ({}) AS sub, bbox
                   WHERE ST_Intersects(geom, bbox)),

     rast_b    AS (SELECT ST_AsRaster(geom, rast, '8BUI', {}) AS rast
                   FROM features, rast_a
                   WHERE NOT ST_IsEmpty(geom))

SELECT ST_AsBinary(ST_MapAlgebra(rast_a.rast, rast_b.rast, '{}', NULL, 'FIRST')) AS wkb FROM rast_a, rast_b

""".format(
                s, w, e, n, srid, s, w, e, n, tile_size, tile_size, tile_size, args.postgis, burn_value, burn_value
            )

            try:
                pg.execute(query)
                row = pg.fetchone()
                if row:
                    raster = np.squeeze(wkb_to_numpy(io.BytesIO(row[0])), axis=2)

            except Exception:
                log.log("Warning: Invalid geometries, skipping {}".format(tile))
                pg_conn = psycopg2.connect(config["dataset"]["pg_dsn"])
                pg = pg_conn.cursor()

            try:
                tile_label_to_file(args.out, tile, colors, raster)
            except:
                log.log("Warning: Unable to rasterize tile. Skipping {}".format(str(tile)))

    if not args.no_web_ui:
        template = "leaflet.html" if not args.web_ui_template else args.web_ui_template
        base_url = args.web_ui_base_url if args.web_ui_base_url else "./"
        tiles = [tile for tile in tiles_from_csv(args.cover)]
        web_ui(args.out, base_url, tiles, tiles, "png", template)

from rasterio.crs import CRS
from rasterio.warp import transform
from rasterio.features import rasterize
from rasterio.transform import from_bounds

import mercantile
from supermercado import burntiles

from robosat_pink.tiles import tile_bbox


def geojson_reproject(feature, srid_in, srid_out):
    """Reproject GeoJSON Polygon feature coords
       Inspired by: https://gist.github.com/dnomadb/5cbc116aacc352c7126e779c29ab7abe
    """

    if feature["geometry"]["type"] == "Polygon":
        xys = (zip(*ring) for ring in feature["geometry"]["coordinates"])
        xys = (list(zip(*transform(CRS.from_epsg(srid_in), CRS.from_epsg(srid_out), *xy))) for xy in xys)

        yield {"coordinates": list(xys), "type": "Polygon"}


def geojson_parse_feature(zoom, srid, feature_map, feature):
    def geojson_parse_polygon(zoom, srid, feature_map, polygon):

        if srid != 4326:
            polygon = [xy for xy in geojson_reproject({"type": "feature", "geometry": polygon}, srid, 4326)][0]

        for i, ring in enumerate(polygon["coordinates"]):  # GeoJSON coordinates could be N dimensionals
            polygon["coordinates"][i] = [[x, y] for point in ring for x, y in zip([point[0]], [point[1]])]

        if polygon["coordinates"]:
            for tile in burntiles.burn([{"type": "feature", "geometry": polygon}], zoom=zoom):
                feature_map[mercantile.Tile(*tile)].append({"type": "feature", "geometry": polygon})

        return feature_map

    def geojson_parse_geometry(zoom, srid, feature_map, geometry):

        if geometry["type"] == "Polygon":
            feature_map = geojson_parse_polygon(zoom, srid, feature_map, geometry)

        elif geometry["type"] == "MultiPolygon":
            for polygon in geometry["coordinates"]:
                feature_map = geojson_parse_polygon(zoom, srid, feature_map, {"type": "Polygon", "coordinates": polygon})

        return feature_map

    if feature["geometry"]["type"] == "GeometryCollection":
        for geometry in feature["geometry"]["geometries"]:
            feature_map = geojson_parse_geometry(zoom, srid, feature_map, geometry)
    else:
        feature_map = geojson_parse_geometry(zoom, srid, feature_map, feature["geometry"])

    return feature_map


def geojson_srid(feature_collection):

    try:
        crs_mapping = {"CRS84": "4326", "900913": "3857"}
        srid = feature_collection["crs"]["properties"]["name"].split(":")[-1]
        srid = int(srid) if srid not in crs_mapping else int(crs_mapping[srid])
    except:
        srid = int(4326)

    return srid


def geojson_tile_burn(tile, features, srid, ts, burn_value=1):
    """Burn tile with GeoJSON features."""

    shapes = ((geometry, burn_value) for feature in features for geometry in geojson_reproject(feature, srid, 3857))

    bounds = tile_bbox(tile, mercator=True)
    transform = from_bounds(*bounds, ts, ts)

    try:
        return rasterize(shapes, out_shape=(ts, ts), transform=transform)
    except:
        return None

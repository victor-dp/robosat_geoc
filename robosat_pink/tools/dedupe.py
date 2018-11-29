import json
import argparse
import functools

import geojson
from tqdm import tqdm

import shapely.geometry

from robosat_pink.vectors import make_index, iou


def add_parser(subparser):
    parser = subparser.add_parser(
        "dedupe", help="deduplicates geojson features", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--threshold", type=float, required=True, help="maximum allowed IoU to keep predictions, between 0.0 and 1.0"
    )
    parser.add_argument("geojson_a", type=str, help="path to a first GeoJSON file")
    parser.add_argument("geojson_b", type=str, help="path to a second GeoJSON file")
    parser.add_argument("out", type=str, help="path to GeoJSON to save deduplicated features to")

    parser.set_defaults(func=main)


def main(args):
    with open(args.geojson_a) as fp:
        features_a = json.load(fp)

    # TODO: at the moment we load all shapes. It would be more efficient to tile
    #       cover and load only A shapes in the tiles covering the B shapes.
    features_a = [shapely.geometry.shape(feature["geometry"]) for feature in features_a["features"]]
    del features_a

    with open(args.geojson_b) as fp:
        features_b = json.load(fp)

    features_b_shapes = [shapely.geometry.shape(features["geometry"]) for features in features_b["features"]]
    del features_b

    idx = make_index(features_a_shapes)
    features = []

    for features_b_shape in tqdm(features_b_shapes, desc="Deduplicating", unit="shapes", ascii=True):
        nearby = [features_a_shapes[i] for i in idx.intersection(features_b_shape.bounds, objects=False)]

        keep = False

        if not nearby:
            keep = True
        else:
            intersecting = [shape for shape in nearby if features_b_shape.intersects(shape)]

            if not intersecting:
                keep = True
            else:
                intersecting_shapes = functools.reduce(lambda lhs, rhs: lhs.union(rhs), intersecting)

                if iou(predicted_shape, intersecting_shapes) < args.threshold:
                    keep = True

        if keep:
            features.append(geojson.Feature(geometry=shapely.geometry.mapping(features_b_shape)))

    collection = geojson.FeatureCollection(features)

    with open(args.out, "w") as fp:
        geojson.dump(collection, fp)

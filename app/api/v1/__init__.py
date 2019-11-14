
from flask import Blueprint
from app.api.v1 import test, predict_buildings, buia, train, predict, wmts, geojson, tools


def create_blueprint_v1():
    bp_v1 = Blueprint('v1', __name__)

    buia.api.register(bp_v1)
    predict.api.register(bp_v1)
    predict_buildings.api.register(bp_v1)
    test.api.register(bp_v1)
    train.api.register(bp_v1)
    wmts.api.register(bp_v1)
    geojson.api.register(bp_v1)
    tools.api.register(bp_v1)

    return bp_v1

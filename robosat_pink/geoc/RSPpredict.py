import os
from robosat_pink.tools import cover, download, rasterize, predict, vectorize
import time
import shutil
import json
from robosat_pink.geoc import config as CONFIG, params


def main(extent, dataPath, dsPath, map="tdt", auto_delete=False):
    params_cover = params.Cover(
        bbox=extent,
        zoom=18, out=[dsPath + "/cover"])
    cover.main(params_cover)

    params_download = params.Download(
        type="XYZ",
        url=CONFIG.WMTS_HOST+"/{z}/{x}/{y}?type="+map,
        cover=dsPath + "/cover",
        out=dsPath + "/images",
        timeout=20)
    download.main(params_download)

    params_predict = params.Predict(
        dataset=dsPath,
        checkpoint=dataPath+'/model/checkpoint-00010.pth',
        config=dataPath+"/config.toml",
        out=dsPath + "/masks"
    )
    predict.main(params_predict)

    params_vectorize = params.Vectorize(
        masks=dsPath + "/masks",
        type="Building",
        config=dataPath+"/config.toml",
        out=dsPath + "/vectors.json"
    )
    vectorize.main(params_vectorize)

    # 解析预测结果并返回
    jsonFile = open(dsPath + "/vectors.json", 'r')
    jsonObj = json.load(jsonFile)

    if auto_delete:
        shutil.rmtree(dsPath)

    return jsonObj

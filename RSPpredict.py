from robosat_pink.tools import params, cover, download, rasterize, predict, vectorize
import time
import shutil
import json


def main(extent, rs_host="http://localhost:7001", map="tdt", auto_delete=False):
    # rsp cover --bbox 4.795,45.628,4.935,45.853 --zoom 18 ds/cover 4.842052459716797,45.76126587962455,4.854111671447754,45.770336923575734
    # rsp download --type XYZ 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}' dp/cover dp/images
    # rsp rasterize --config data/config.toml --type Building --geojson data/buildings.json  --cover dp/cover dp/labels
    # rsp predict --checkpoint data/model/checkpoint-0.00005.pth ds dp/masks
    # rsp vectorize --type --config masks out

    ts = time.time()
    path = "ds/predict" + str(ts)

    params_cover = params.Cover(
        bbox=extent,
        zoom=18, out=[path + "/cover"])
    cover.main(params_cover)

    params_download = params.Download(
        type="XYZ",
        url=rs_host+"/wmts/{z}/{x}/{y}?type="+map,
        cover=path + "/cover",
        out=path + "/images",
        timeout=20)
    download.main(params_download)

    params_predict = params.Predict(
        dataset=path,
        checkpoint='data/model/checkpoint-00010.pth',
        config="data/config.toml",
        out=path + "/masks"
    )
    predict.main(params_predict)

    params_vectorize = params.Vectorize(
        masks=path + "/masks",
        type="Building",
        config="data/config.toml",
        out=path + "/vectors.json"
    )
    vectorize.main(params_vectorize)

    # 解析预测结果并返回
    jsonFile = open(path + "/vectors.json", 'r')
    jsonObj = json.load(jsonFile)

    if auto_delete:
        shutil.rmtree(path)

    return jsonObj

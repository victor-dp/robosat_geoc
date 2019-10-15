import os
import sys
import shutil
from robosat_pink.tools import params, cover, download, rasterize, subset, train
import multiprocessing
import config
multiprocessing.set_start_method('spawn', True)


def main(extent, sql, rs_host="http://localhost:7001", type="tdt"):
    # example
    # rsp cover --bbox 4.795,45.628,4.935,45.853 --zoom 18 ds/cover
    # rsp download --type WMS 'https://download.data.grandlyon.com/wms/grandlyon?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=Ortho2015_vue_ensemble_16cm_CC46&WIDTH=512&HEIGHT=512&CRS=EPSG:3857&BBOX={xmin},{ymin},{xmax},{ymax}&FORMAT=image/jpeg' ds/cover ds/images
    # rsp rasterize --config ds/config.toml --type Building --geojson ds/lyon_roofprint.json --cover ds/cover ds/labels
    # rsp cover --dir ds/images --splits 70/30 ds/training/cover ds/validation/cover

    # clear ds directory at first
    # if os.path.isdir('./ds'):
    #     shutil.rmtree("./ds")

    # params_cover = params.Cover(
    #     # bbox="4.842052459716797,45.76126587962455,4.854111671447754,45.770336923575734",
    #     bbox=extent,
    #     zoom=18, out=["ds/cover"])
    # cover.main(params_cover)

    # params_download = params.Download(
    #     url=rs_host+"/wmts/{z}/{x}/{y}?type="+type,
    #     cover="ds/cover",
    #     out="ds/images")
    # download.main(params_download)

    params_rasterize = params.Rasterize(
        config="data/config.toml",
        type="Building",
        ts=256,
        # geojson=["data/buildings.json"],
        pg=config.pg,
        sql=sql,
        cover="ds/cover",
        out="ds/labels"
    )
    rasterize.main(params_rasterize)

    # params_cover2 = params.Cover(
    #     dir='ds/images',
    #     splits='70/30',
    #     out=['ds/training/cover', 'ds/validation/cover']
    # )
    # cover.main(params_cover2)

    # params_subset_train_images = params.Subset(
    #     dir='ds/images',
    #     cover='ds/training/cover',
    #     out='ds/training/images'
    # )
    # subset.main(params_subset_train_images)

    # params_subset_train_labels = params.Subset(
    #     dir='ds/labels',
    #     cover='ds/training/cover',
    #     out='ds/training/labels'
    # )
    # subset.main(params_subset_train_labels)

    # params_subset_validation_images = params.Subset(
    #     dir='ds/images',
    #     cover='ds/validation/cover',
    #     out='ds/validation/images'
    # )
    # subset.main(params_subset_validation_images)

    # params_subset_validation_labels = params.Subset(
    #     dir='ds/labels',
    #     cover='ds/validation/cover',
    #     out='ds/validation/labels'
    # )
    # subset.main(params_subset_validation_labels)

    # params_train = params.Train(
    #     config='data/config.toml',
    #     epochs=10,
    #     ts=(256, 256),
    #     dataset='ds',
    #     out='ds/model'
    # )
    # train.main(params_train)

    sys.exit(0)

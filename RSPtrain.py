import os
import sys
import shutil
from robosat_geoc.robosat_pink.tools import params, cover, download, rasterize, subset, train
import multiprocessing
from robosat_geoc import config
import time
multiprocessing.set_start_method('spawn', True)


def main(extent, rs_host="http://localhost:5000/v1/wmts", map="tdt", auto_delete=False):
    # example
    # rsp cover --bbox 4.795,45.628,4.935,45.853 --zoom 18 ds/cover
    # rsp download --type WMS 'https://download.data.grandlyon.com/wms/grandlyon?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=Ortho2015_vue_ensemble_16cm_CC46&WIDTH=512&HEIGHT=512&CRS=EPSG:3857&BBOX={xmin},{ymin},{xmax},{ymax}&FORMAT=image/jpeg' ds/cover ds/images
    # rsp rasterize --config ds/config.toml --type Building --geojson ds/lyon_roofprint.json --cover ds/cover ds/labels
    # rsp cover --dir ds/images --splits 70/30 ds/training/cover ds/validation/cover

    # clear ds directory at first

    ts = time.time()
    path = "ds/train_"+str(ts)

    params_cover = params.Cover(
        bbox=extent,
        zoom=18, out=[path + "/cover"])
    cover.main(params_cover)

    params_download = params.Download(
        type="XYZ",
        url=rs_host+"/{z}/{x}/{y}?type="+map,
        cover=path + "/cover",
        out=path + "/images")
    download.main(params_download)

    params_rasterize = params.Rasterize(
        config=os.getcwd()+'/robosat_geoc/'+"data/config.toml",
        type="Building",
        ts=256, 
        # geojson=["data/buildings.json"],
        pg=config.pg,
        sql='SELECT geom FROM "'+config.building_table + \
            '" WHERE ST_Intersects(TILE_GEOM, geom)',
        cover=path + "/cover",
        out=path + "/labels"
    ) 
    rasterize.main(params_rasterize)

    params_cover2 = params.Cover(
        dir=path+'/images',
        splits='70/30',
        out=[path+'/training/cover', path+'/validation/cover']
    )
    cover.main(params_cover2)

    params_subset_train_images = params.Subset(
        dir=path+'/images',
        cover=path+'/training/cover',
        out=path+'/training/images'
    )
    subset.main(params_subset_train_images)

    params_subset_train_labels = params.Subset(
        dir=path+'/labels',
        cover=path+'/training/cover',
        out=path+'/training/labels'
    )
    subset.main(params_subset_train_labels)

    params_subset_validation_images = params.Subset(
        dir=path+'/images',
        cover=path+'/validation/cover',
        out=path+'/validation/images'
    )
    subset.main(params_subset_validation_images)

    params_subset_validation_labels = params.Subset(
        dir=path+'/labels',
        cover=path+'/validation/cover',
        out=path+'/validation/labels'
    )
    subset.main(params_subset_validation_labels)

    params_train = params.Train(
        config=os.getcwd()+'/robosat_geoc/'+'data/config.toml',
        epochs=10,
        ts=(256, 256),
        dataset=path,
        checkpoint=os.getcwd()+'/'+"data/model/checkpoint-00010.pth",
        out='data/model'
    )
    train.main(params_train)

    if auto_delete:
        shutil.rmtree(path)
# 2 mins
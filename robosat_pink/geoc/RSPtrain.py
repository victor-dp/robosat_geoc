import os
import sys
import shutil
import multiprocessing

from robosat_pink.tools import cover, download, rasterize, subset, train
from robosat_pink.geoc import config as CONFIG, params

multiprocessing.set_start_method('spawn', True)


def main(extent, dataPath, dsPath,  map="tdt", auto_delete=False):

    params_cover = params.Cover(
        bbox=extent,
        zoom=18, out=[dsPath + "/cover"])
    cover.main(params_cover)

    params_download = params.Download(
        type="XYZ",
        url=CONFIG.WMTS_HOST+"/{z}/{x}/{y}?type="+map,
        cover=dsPath + "/cover",
        out=dsPath + "/images")
    download.main(params_download)

    params_rasterize = params.Rasterize(
        config=dataPath+"/config.toml",
        type="Building",
        ts=256,
        pg=CONFIG.POSTGRESQL,
        sql='SELECT geom FROM "'+CONFIG.BUILDING_TABLE +
            '" WHERE ST_Intersects(TILE_GEOM, geom)',
        cover=dsPath + "/cover",
        out=dsPath + "/labels"
    )
    rasterize.main(params_rasterize)

    params_cover2 = params.Cover(
        dir=dsPath+'/images',
        splits='70/30',
        out=[dsPath+'/training/cover', dsPath+'/validation/cover']
    )
    cover.main(params_cover2)

    params_subset_train_images = params.Subset(
        dir=dsPath+'/images',
        cover=dsPath+'/training/cover',
        out=dsPath+'/training/images'
    )
    subset.main(params_subset_train_images)

    params_subset_train_labels = params.Subset(
        dir=dsPath+'/labels',
        cover=dsPath+'/training/cover',
        out=dsPath+'/training/labels'
    )
    subset.main(params_subset_train_labels)

    params_subset_validation_images = params.Subset(
        dir=dsPath+'/images',
        cover=dsPath+'/validation/cover',
        out=dsPath+'/validation/images'
    )
    subset.main(params_subset_validation_images)

    params_subset_validation_labels = params.Subset(
        dir=dsPath+'/labels',
        cover=dsPath+'/validation/cover',
        out=dsPath+'/validation/labels'
    )
    subset.main(params_subset_validation_labels)

    params_train = params.Train(
        config=dataPath+'/config.toml',
        epochs=10,
        ts=(256, 256),
        dataset=dsPath,
        # checkpoint=dataPath+"/model/checkpoint-00010.pth",
        out=dataPath+'/model'
    )
    train.main(params_train)

    if auto_delete:
        shutil.rmtree(dsPath)
# 2 mins

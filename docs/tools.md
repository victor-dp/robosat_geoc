# RoboSat.pink tools documentation
## rsp compare
```
usage: rsp compare [-h] [--mode {side,stack,list}] [--labels LABELS]
                   [--masks MASKS] [--images IMAGES [IMAGES ...]]
                   [--workers WORKERS] [--minimum_fg MINIMUM_FG]
                   [--maximum_fg MAXIMUM_FG] [--minimum_qod MINIMUM_QOD]
                   [--maximum_qod MAXIMUM_QOD] [--vertical] [--geojson]
                   [--format FORMAT] [--web_ui_base_url WEB_UI_BASE_URL]
                   [--web_ui_template WEB_UI_TEMPLATE] [--no_web_ui]
                   out

optional arguments:
 -h, --help                         show this help message and exit

Inputs:
 --mode {side,stack,list}           compare mode [default: side]
 --labels LABELS                    path to tiles labels directory [required for QoD filtering]
 --masks MASKS                      path to tiles masks directory [required for QoD filtering)
 --images IMAGES [IMAGES ...]       path to images directories [required for stack or side modes]
 --workers WORKERS                  number of workers [default: CPU / 2]

QoD Filtering:
 --minimum_fg MINIMUM_FG            skip tile if label foreground below. [default: 0]
 --maximum_fg MAXIMUM_FG            skip tile if label foreground above [default: 100]
 --minimum_qod MINIMUM_QOD          skip tile if QoD metric below [default: 0]
 --maximum_qod MAXIMUM_QOD          skip tile if QoD metric above [default: 100]

Outputs:
 --vertical                         output vertical image aggregate [optionnal for side mode]
 --geojson                          output results as GeoJSON [optionnal for list mode]
 --format FORMAT                    output images file format [default: webp]
 out                                output path

Web UI:
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
 --no_web_ui                        desactivate Web UI output
```
## rsp cover
```
usage: rsp cover [-h] [--dir DIR] [--bbox BBOX] [--geojson GEOJSON]
                 [--raster RASTER] [--zoom ZOOM] [--splits SPLITS]
                 out [out ...]

optional arguments:
 -h, --help         show this help message and exit

Input [one among the following is required]:
 --dir DIR          XYZ tiles dir path
 --bbox BBOX        a lat/lon bbox: xmin,ymin,xmax,ymax or a bbox: xmin,xmin,xmax,xmax,EPSG:xxxx
 --geojson GEOJSON  a geojson file path
 --raster RASTER    a raster file path

Outputs:
 --zoom ZOOM        zoom level of tiles [required with --geojson or --bbox]
 --splits SPLITS    if set, shuffle and split in several cover subpieces. [e.g 50,15,35]
 out                cover csv output paths [required]
```
## rsp download
```
usage: rsp download [-h] [--type {XYZ,WMS,TMS}] [--rate RATE]
                    [--timeout TIMEOUT] [--workers WORKERS] [--format FORMAT]
                    [--web_ui_base_url WEB_UI_BASE_URL]
                    [--web_ui_template WEB_UI_TEMPLATE] [--no_web_ui]
                    url cover out

optional arguments:
 -h, --help                         show this help message and exit

Web Server:
 url                                URL server endpoint, with: {z}/{x}/{y} or {xmin},{ymin},{xmax},{ymax} [required]
 --type {XYZ,WMS,TMS}               service type [default: XYZ]
 --rate RATE                        download rate limit in max requests/seconds [default: 10]
 --timeout TIMEOUT                  download request timeout (in seconds) [default: 10]
 --workers WORKERS                  number of workers [default: CPU / 2]

Coverage to download:
 cover                              path to .csv tiles list [required]

Output:
 --format FORMAT                    file format to save images in [default: webp]
 out                                output directory path [required]

Web UI:
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
 --no_web_ui                        desactivate Web UI output
```
## rsp export
```
usage: rsp export [-h] --checkpoint CHECKPOINT [--type {onnx,jit}]
                  [--config CONFIG]
                  out

optional arguments:
 -h, --help               show this help message and exit

Inputs:
 --checkpoint CHECKPOINT  model checkpoint to load [required]
 --type {onnx,jit}        output type [default: jit]
 --config CONFIG          path to config file [required]

Output:
 out                      path to save export model to [required]
```
## rsp extract
```
usage: rsp extract [-h] --type TYPE pbf out

optional arguments:
 -h, --help   show this help message and exit

Inputs:
 --type TYPE  type of feature to extract (e.g building, road) [required]
 pbf          path to .osm.pbf file [required]

Output:
 out          GeoJSON output file path [required]
```
## rsp predict
```
usage: rsp predict [-h] --checkpoint CHECKPOINT [--config CONFIG]
                   [--model MODEL] [--tile_size TILE_SIZE]
                   [--tile_overlap TILE_OVERLAP] [--workers WORKERS]
                   [--batch_size BATCH_SIZE]
                   [--web_ui_base_url WEB_UI_BASE_URL]
                   [--web_ui_template WEB_UI_TEMPLATE] [--no_web_ui]
                   tiles out

optional arguments:
 -h, --help                         show this help message and exit

Inputs:
 tiles                              tiles directory path [required]
 --checkpoint CHECKPOINT            path to the trained model to use [required]
 --config CONFIG                    path to config file [required]
 --model MODEL                      if set, override model name from config file
 --tile_size TILE_SIZE              if set, override tile size value from config file
 --tile_overlap TILE_OVERLAP        tile pixels overlap [default: 64]

Outputs:
 out                                output directory path [required]

Performances:
 --workers WORKERS                  number of workers to load images [default: GPU x 2]
 --batch_size BATCH_SIZE            if set, override batch_size value from config file

Web UI:
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
 --no_web_ui                        desactivate Web UI output
```
## rsp rasterize
```
usage: rsp rasterize [-h] [--postgis POSTGIS] [--geojson GEOJSON]
                     [--config CONFIG] [--tile_size TILE_SIZE]
                     [--web_ui_base_url WEB_UI_BASE_URL]
                     [--web_ui_template WEB_UI_TEMPLATE] [--no_web_ui]
                     cover out

optional arguments:
 -h, --help                         show this help message and exit

Inputs [either --postgis or --geojson is required]:
 cover                              path to csv tiles cover file [required]
 --postgis POSTGIS                  SELECT query to retrieve geometry features [e.g SELECT geom FROM table]
 --geojson GEOJSON                  path to GeoJSON features files [e.g /foo/bar/*.json] 
 --config CONFIG                    path to config file [required]

Outputs:
 out                                output directory path [required]
 --tile_size TILE_SIZE              output tile size [default: 512]

Web UI:
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
 --no_web_ui                        desactivate Web UI output
```
## rsp subset
```
usage: rsp subset [-h] --dir DIR --filter FILTER [--move MOVE]
                  [--delete DELETE] [--web_ui_base_url WEB_UI_BASE_URL]
                  [--web_ui_template WEB_UI_TEMPLATE] [--no_web_ui]
                  [out]

optional arguments:
 -h, --help                         show this help message and exit

Inputs:
 --dir DIR                          to XYZ tiles input dir path [required]
 --filter FILTER                    path to csv cover file to filter dir by [required]

Alternate modes, as default is to copy.:
 --move MOVE                        move filtered tiles from input to output
 --delete DELETE                    delete filtered tiles

Output:
 out                                output dir path [required for copy or move]

Web UI:
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
 --no_web_ui                        desactivate Web UI output
```
## rsp tile
```
usage: rsp tile [-h] [--config CONFIG] [--no_data NO_DATA]
                [--type {image,label}] --zoom ZOOM [--tile_size TILE_SIZE]
                [--web_ui_base_url WEB_UI_BASE_URL]
                [--web_ui_template WEB_UI_TEMPLATE] [--no_web_ui]
                raster out

optional arguments:
 -h, --help                         show this help message and exit

Inputs:
 raster                             path to the raster to tile [required]
 --config CONFIG                    path to config file [required in label mode]
 --no_data NO_DATA                  no data value [0-255]. If set, skip tile with at least one no data border

Output:
 out                                output directory path [required]
 --type {image,label}               image or label tiling [default: image]
 --zoom ZOOM                        zoom level of tiles [required]
 --tile_size TILE_SIZE              tile size in pixels [default: 512]

Web UI:
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
 --no_web_ui                        desactivate Web UI output
```
## rsp train
```
usage: rsp train [-h] [--config CONFIG] [--loader LOADER] [--workers WORKERS]
                 [--batch_size BATCH_SIZE] [--lr LR] [--model MODEL]
                 [--loss LOSS] [--epochs EPOCHS] [--resume]
                 [--checkpoint CHECKPOINT]
                 dataset out

optional arguments:
 -h, --help               show this help message and exit
 --config CONFIG          path to config file [required]

Dataset:
 dataset                  training dataset path
 --loader LOADER          dataset loader name [if set override config file value]
 --workers WORKERS        number of pre-processing images workers [default: GPUs x 2]

Hyper Parameters [if set override config file value]:
 --batch_size BATCH_SIZE  batch_size
 --lr LR                  learning rate
 --model MODEL            model name
 --loss LOSS              model loss

Model Training:
 --epochs EPOCHS          number of epochs to train [default 10]
 --resume                 resume model training, if set imply to provide a checkpoint
 --checkpoint CHECKPOINT  path to a model checkpoint. To fine tune or resume a training

Output:
 out                      output directory path to save checkpoint .pth files and logs [required]
```
## rsp vectorize
```
usage: rsp vectorize [-h] --type TYPE [--config CONFIG] masks out

optional arguments:
 -h, --help       show this help message and exit

Inputs:
 masks            input masks directory path [required]
 --type TYPE      type of features to extract (i.e class title) [required]
 --config CONFIG  path to config file [required]

Outputs:
 out              path to GeoJSON file to store features in [required]
```

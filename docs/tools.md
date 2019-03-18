# RoboSat.pink tools documentation
## rsp compare
```
usage: rsp compare [-h] [--mode {side,stack,list}] [--config CONFIG]
                   [--labels LABELS] [--masks MASKS]
                   [--images IMAGES [IMAGES ...]] [--minimum_fg MINIMUM_FG]
                   [--maximum_fg MAXIMUM_FG] [--minimum_qod MINIMUM_QOD]
                   [--maximum_qod MAXIMUM_QOD] [--vertical] [--geojson]
                   [--format FORMAT] [--web_ui]
                   [--web_ui_base_url WEB_UI_BASE_URL]
                   [--web_ui_template WEB_UI_TEMPLATE]
                   out

optional arguments:
 -h, --help                         show this help message and exit

Inputs:
 --mode {side,stack,list}           compare mode [default: side]
 --config CONFIG                    path to configuration file [required for QoD filtering]
 --labels LABELS                    path to tiles labels directory [required for QoD filtering]
 --masks MASKS                      path to tiles masks directory [required for QoD filtering)
 --images IMAGES [IMAGES ...]       path to images directories [required for stack or side modes]

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
 --web_ui                           activate Web UI output
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
```
## rsp cover
```
usage: rsp cover [-h] [--type {geojson,bbox,dir}] [--zoom ZOOM]
                 [--splits SPLITS]
                 input out [out ...]

optional arguments:
 -h, --help                 show this help message and exit

Inputs:
 --type {geojson,bbox,dir}  input type [default: geojson]
 input                      upon input type: a geojson file path, a lat/lon bbox or a XYZ tiles dir path [required]

Outputs:
 --zoom ZOOM                zoom level of tiles [required for geojson or bbox modes]
 --splits SPLITS            if set, shuffle and split in several cover pieces. [e.g 50,15,35]
 out                        cover csv output paths [required]
```
## rsp download
```
usage: rsp download [-h] [--type {XYZ,WMS,TMS}] [--rate RATE]
                    [--timeout TIMEOUT] [--format FORMAT] [--web_ui]
                    [--web_ui_base_url WEB_UI_BASE_URL]
                    [--web_ui_template WEB_UI_TEMPLATE]
                    url tiles out

optional arguments:
 -h, --help                         show this help message and exit

Web Server:
 url                                url server endpoint to fetch image tiles [required]
 --type {XYZ,WMS,TMS}               service type [default: XYZ]
 --rate RATE                        download rate limit in max requests/seconds [default: 10]
 --timeout TIMEOUT                  download request timeout (in seconds) [default: 10]

Coverage to download:
 tiles                              path to .csv tiles list [required]

Output:
 --format FORMAT                    file format to save images in [default: webp]
 out                                output directory path [required]

Web UI:
 --web_ui                           activate Web UI output
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
```
## rsp extract
```
usage: rsp extract [-h] --type TYPE pbf out

optional arguments:
 -h, --help   show this help message and exit

Inputs:
 --type TYPE  type of feature to extract [required]
 pbf          path to .osm.pbf file [required]

Output:
 out          path to GeoJSON file to store features in [required]
```
## rsp predict
```
usage: rsp predict [-h] --config CONFIG --checkpoint CHECKPOINT
                   [--model MODEL] [--tile_size TILE_SIZE]
                   [--tile_overlap TILE_OVERLAP] [--workers WORKERS]
                   [--batch_size BATCH_SIZE] [--web_ui]
                   [--web_ui_base_url WEB_UI_BASE_URL]
                   [--web_ui_template WEB_UI_TEMPLATE]
                   tiles out

optional arguments:
 -h, --help                         show this help message and exit

Inputs:
 tiles                              tiles directory path [required]
 --config CONFIG                    path to configuration file [required]
 --checkpoint CHECKPOINT            path to the trained model to use [required]
 --model MODEL                      if set, override model name from config file
 --tile_size TILE_SIZE              if set, override tile size value from config file
 --tile_overlap TILE_OVERLAP        tile pixels overlap [default: 64]

Outputs:
 out                                output directory path [required]

Performances:
 --workers WORKERS                  number of workers to load images [default: GPU x 2]
 --batch_size BATCH_SIZE            if set, override batch_size value from config file

Web UI:
 --web_ui                           activate Web UI output
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
```
## rsp rasterize
```
usage: rsp rasterize [-h] --config CONFIG [--postgis POSTGIS]
                     [--geojson GEOJSON [GEOJSON ...]] [--tile_size TILE_SIZE]
                     [--web_ui] [--web_ui_base_url WEB_UI_BASE_URL]
                     [--web_ui_template WEB_UI_TEMPLATE]
                     cover out

optional arguments:
 -h, --help                         show this help message and exit

Inputs:
 cover                              path to csv tiles cover file [mandatory]
 --config CONFIG                    path to configuration file [mandatory]
 --postgis POSTGIS                  PostGIS SQL SELECT query to retrieve features
 --geojson GEOJSON [GEOJSON ...]    path to GeoJSON features files

Outputs:
 out                                output directory path [mandatory]
 --tile_size TILE_SIZE              if set, override tile size value from config file

Web UI:
 --web_ui                           activate Web UI output
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
```
## rsp subset
```
usage: rsp subset [-h] [--mode {move,copy,delete}] --dir DIR --cover COVER
                  [--out OUT] [--web_ui] [--web_ui_base_url WEB_UI_BASE_URL]
                  [--web_ui_template WEB_UI_TEMPLATE]

optional arguments:
 -h, --help                         show this help message and exit

Inputs:
 --mode {move,copy,delete}          subset mode [default: copy]
 --dir DIR                          path to inputs XYZ tiles dir [mandatory]
 --cover COVER                      path to csv cover file to subset tiles by [mandatory]

Output:
 --out OUT                          output directory path [mandatory for copy or move mode]

Web UI:
 --web_ui                           activate Web UI output
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
```
## rsp tile
```
usage: rsp tile [-h] --config CONFIG [--no_data NO_DATA]
                [--type {image,label}] --zoom ZOOM [--tile_size TILE_SIZE]
                [--web_ui] [--web_ui_base_url WEB_UI_BASE_URL]
                [--web_ui_template WEB_UI_TEMPLATE]
                raster out

optional arguments:
 -h, --help                         show this help message and exit

Inputs:
 raster                             path to the raster to tile [required]
 --config CONFIG                    path to the configuration file [required]
 --no_data NO_DATA                  color considered as no data [0-255]. If set, skip related tile

Output:
 out                                output directory path [required]
 --type {image,label}               image or label tiling [default: image]
 --zoom ZOOM                        zoom level of tiles [required]
 --tile_size TILE_SIZE              tile size in pixels [default: 512]

Web UI:
 --web_ui                           activate Web UI output
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
```
## rsp train
```
usage: rsp train [-h] --config CONFIG [--dataset DATASET]
                 [--batch_size BATCH_SIZE] [--lr LR] [--model MODEL]
                 [--loss LOSS] [--epochs EPOCHS] [--resume]
                 [--checkpoint CHECKPOINT] [--workers WORKERS]
                 out

optional arguments:
 -h, --help               show this help message and exit

Hyper Parameters:
 --config CONFIG          path to configuration file [required]
 --dataset DATASET        if set, override dataset path value from config file
 --batch_size BATCH_SIZE  if set, override batch_size value from config file
 --lr LR                  if set, override learning rate value from config file
 --model MODEL            if set, override model name from config file
 --loss LOSS              if set, override model loss from config file

Output:
 out                      output directory path to save checkpoint .pth files and logs [required]

Model Training:
 --epochs EPOCHS          number of epochs to train [default 10]
 --resume                 resume model training, if set imply to provide a checkpoint
 --checkpoint CHECKPOINT  path to a model checkpoint. To fine tune, or resume training if setted

Performances:
 --workers WORKERS        number pre-processing images workers. [default: GPU x 2]
```
## rsp vectorize
```
usage: rsp vectorize [-h] --type TYPE --config CONFIG masks out

optional arguments:
 -h, --help       show this help message and exit

Inputs:
 masks            input masks directory path [required]
 --type TYPE      type of features to extract (i.e class title) [required]
 --config CONFIG  path to configuration file [required]

Outputs:
 out              path to GeoJSON file to store features in [required]
```

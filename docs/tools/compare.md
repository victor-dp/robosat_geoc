# rsp compare
```
usage: rsp compare [-h] [--mode {side,stack,list}] [--config CONFIG]
                   [--labels LABELS] [--masks MASKS]
                   [--images IMAGES [IMAGES ...]] [--minimum_fg MINIMUM_FG]
                   [--maximum_fg MAXIMUM_FG] [--minimum_qod MINIMUM_QOD]
                   [--maximum_qod MAXIMUM_QOD] [--vertical] [--geojson]
                   [--ext EXT] [--web_ui] [--web_ui_base_url WEB_UI_BASE_URL]
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
 --ext EXT                          output images file format [default: webp]
 out                                output path

Web UI:
 --web_ui                           activate Web UI output
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
```

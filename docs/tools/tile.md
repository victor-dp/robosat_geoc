# rsp tile
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
 --tile_size TILE_SIZE              if set, override tiles side in pixels, from config file

Web UI:
 --web_ui                           activate Web UI output
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
```

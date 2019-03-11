# rsp rasterize
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

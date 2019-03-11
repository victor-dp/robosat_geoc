# rsp predict
```
usage: rsp predict [-h] --checkpoint CHECKPOINT --config CONFIG
                   [--tile_overlap TILE_OVERLAP] [--tile_size TILE_SIZE]
                   [--ext_path EXT_PATH] [--workers WORKERS]
                   [--batch_size BATCH_SIZE] [--web_ui]
                   [--web_ui_base_url WEB_UI_BASE_URL]
                   [--web_ui_template WEB_UI_TEMPLATE]
                   tiles probs

optional arguments:
 -h, --help                         show this help message and exit

Inputs:
 tiles                              tiles directory path [required]
 --checkpoint CHECKPOINT            path to trained model to use [required]
 --config CONFIG                    path to configuration file [required]
 --tile_overlap TILE_OVERLAP        tile pixels overlap [default: 64]
 --tile_size TILE_SIZE              if set, override tile size value from config file
 --ext_path EXT_PATH                path to user's extension modules dir. Allow to use alternate models.

Outputs:
 probs                              output directory path [required]

Performances:
 --workers WORKERS                  number of workers to load images [default: 0]
 --batch_size BATCH_SIZE            if set, override batch_size value from config file

Web UI:
 --web_ui                           activate Web UI output
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
```

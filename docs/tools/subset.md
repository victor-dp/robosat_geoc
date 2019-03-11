# rsp subset
```
usage: rsp subset [-h] [--mode {delete,move,copy}] --dir DIR --cover COVER
                  [--out OUT] [--web_ui] [--web_ui_base_url WEB_UI_BASE_URL]
                  [--web_ui_template WEB_UI_TEMPLATE]

optional arguments:
 -h, --help                         show this help message and exit

Inputs:
 --mode {delete,move,copy}          subset mode [default: copy]
 --dir DIR                          path to inputs XYZ tiles dir [mandatory]
 --cover COVER                      path to csv cover file to subset tiles by [mandatory]

Output:
 --out OUT                          output directory path [mandatory for copy or move mode]

Web UI:
 --web_ui                           activate Web UI output
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
```

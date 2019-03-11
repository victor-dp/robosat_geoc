# rsp download
```
usage: rsp download [-h] [--type {XYZ,WMS,TMS}] [--rate RATE]
                    [--timeout TIMEOUT] [--ext EXT] [--web_ui]
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
 --ext EXT                          file format to save images in [default: webp]
 out                                output directory path [required]

Web UI:
 --web_ui                           activate Web UI output
 --web_ui_base_url WEB_UI_BASE_URL  alternate Web UI base URL
 --web_ui_template WEB_UI_TEMPLATE  alternate Web UI template path
```

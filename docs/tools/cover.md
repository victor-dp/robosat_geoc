# rsp cover
```
usage: rsp cover [-h] [--type {geojson,bbox,dir}] [--zoom ZOOM] input out

optional arguments:
 -h, --help                 show this help message and exit

Inputs:
 --type {geojson,bbox,dir}  input type [default: geojson]
 input                      upon input type: a geojson file path, a lat/lon bbox or a XYZ tiles dir path [required]

Outputs:
 --zoom ZOOM                zoom level of tiles [required for geojson or bbox modes]
 out                        cover csv file output path [required]
```

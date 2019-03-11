# rsp extract
```
usage: rsp extract [-h] --type TYPE [--ext_path EXT_PATH] pbf out

optional arguments:
 -h, --help           show this help message and exit

Inputs:
 pbf                  path to .osm.pbf file [required]
 --type TYPE          type of feature to extract [required]
 --ext_path EXT_PATH  path to user's extension modules dir. Allow to use alternate types.

Output:
 out                  path to GeoJSON file to store features in [required]
```

# From OpenData to OpenDataSet


Goals:
-----

Data preparation could be a painful and time consuming task, if you don't use tools abstract and efficient enough.

OpenData became more and more available. But we still lack DataSets good enough to be used to train models.
And at the state of art, best results in model training are achieved by players who can afford to labelize by hand and with pixel accuracy their own dataset.

This tutorial aim is to show you, how you could quite easily retrieve and qualify OpenData with RoboSat.pink in order to create your own training DataSet.



Retrieve OpenData:
------------------

We choose to use OpenData from <a href="https://rdata-grandlyon.readthedocs.io/en/latest/">Grand Lyon metropole</a> because they provide recent imagery and several vector layers throught standardized Web Services.



First step is to define the coverage geospatial extent and a <a href="https://wiki.openstreetmap.org/wiki/Zoom_levels">zoom level</a>:

```
rsp cover --zoom 18 --type bbox 4.795,45.628,4.935,45.853  ~/rsp_dataset/cover
```


Then to download imagery, throught <a href="https://www.opengeospatial.org/standards/wms">WMS</a>,

```
rsp download --type WMS 'https://download.data.grandlyon.com/wms/grandlyon?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=Ortho2015_vue_ensemble_16cm_CC46&WIDTH=512&HEIGHT=512&CRS=EPSG:3857&BBOX={xmin},{ymin},{xmax},{ymax}&FORMAT=image/jpeg' --ext jpeg --web_ui $RSP_URL/images ~/rsp_dataset/cover ~/rsp_dataset/images
```

NOTA:
- Retina resolution of 512px is prefered to a regular 256px, because it will quite obviously improve the training accuracy result. 
- Launch this command again, if any tile download error, till the whole coverage is fully downloaded.



<a href="http://www.datapink.tools/rsp/opendata_to_opendataset/images/"><img src="img/from_opendata_to_opendataset/images.png" /></a>


Then to download buildings vector roof print, throught <a href="https://www.opengeospatial.org/standards/wfs">WFS</a>, 

```
wget -O ~/rsp_dataset/lyon_roofprint.json 'https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=ms:fpc_fond_plan_communaut.fpctoit&VERSION=1.1.0&srsName=EPSG:4326&outputFormat=application/json; subtype=geojson'
```

Roofprint choice is meaningful here, as we use aerial imagery to retrieve patterns. If we use footprint instead, our later training accuracy performances would be poorer. 




Prepare DataSet
----------------

Now you have to transform vector roofprints, to raster labels:

```
rsp rasterize --config config.toml --zoom 18 --web_ui $RSP_URL/labels ~/rsp_dataset/lyon_roofprint.json ~/rsp_dataset/cover ~/rsp_dataset/labels
```

<a href="http://www.datapink.tools/rsp/opendata_to_opendataset/labels/"><img src="img/from_opendata_to_opendataset/labels.png" /></a>


Then to create a training / validation dataset, with imagery and related roofprint labels:

```
mkdir ~/rsp_dataset/training ~/rsp_dataset/validation

cat ~/rsp_dataset/cover | sort -R >  ~/rsp_dataset/cover.shuffled
head -n 16384 ~/rsp_dataset/cover.shuffled > ~/rsp_dataset/training/cover
tail -n 7924  ~/rsp_dataset/cover.shuffled > ~/rsp_dataset/validation/cover

rsp subset --web_ui $RSP_URL/training/images --dir ~/rsp_dataset/images --cover ~/rsp_dataset/training/cover --out ~/rsp_dataset/training/images
rsp subset --web_ui $RSP_URL/training/labels --dir ~/rsp_dataset/labels --cover ~/rsp_dataset/training/cover --out ~/rsp_dataset/training/labels
rsp subset --web_ui $RSP_URL/validation/images --dir ~/rsp_dataset/images --cover ~/rsp_dataset/validation/cover --out ~/rsp_dataset/validation/images
rsp subset --web_ui $RSP_URL/validation/labels --dir ~/rsp_dataset/labels --cover ~/rsp_dataset/validation/cover --out ~/rsp_dataset/validation/labels
```

Two points to emphasize there:
 - It's a good idea to take enough data for the validation part (here we took a 70/30 ratio).
 - The shuffle part help to reduce spatial bias in train/validation sets.


Train
-----

Now to launch a first model train:

```
rsp train --config config.toml ~/rsp_dataset/pth
```

After 10 epochs, the building IoU metric on validation dataset, is **~0.82**. 
It's already a good result, at the state of art, with real world data, but we will see how to increase it.



Predict masks
-------------

```
rsp predict --config config.toml --checkpoint ~/rsp_dataset/pth/checkpoint-00010-of-00010.pth --web_ui $RSP_URL/masks ~/rsp_dataset/images ~/rsp_dataset/masks
```

<a href="http://www.datapink.tools/rsp/opendata_to_opendataset/masks/"><img src="img/from_opendata_to_opendataset/masks.png" /></a>


Compare
```
rsp compare --images ~/rsp_dataset/images ~/rsp_dataset/labels ~/rsp_dataset/masks --mode stack --labels ~/rsp_dataset/labels --masks ~/rsp_dataset/masks --config config.toml --ext jpeg --web_ui $RSP_URL/compare ~/rsp_dataset/compare

rsp compare --mode list --labels ~/rsp_dataset/labels --maximum_qod 80 --minimum_fg 5 --masks ~/rsp_dataset/masks --config config.toml --geojson ~/rsp_dataset/compare/tiles.json
```

<a href="http://www.datapink.tools/rsp/opendata_to_opendataset/compare/"><img src="img/from_opendata_to_opendataset/compare.png" /></a>


```
rsp compare --mode side --images ~/rsp_dataset/images ~/rsp_dataset/compare --labels ~/rsp_dataset/labels --maximum_qod 80 --minimum_fg 5 --masks ~/rsp_dataset/masks --config config.toml --ext jpeg --web_ui $RSP_URL/compare_side ~/rsp_dataset/compare_side
```

<a href="http://www.datapink.tools/rsp/opendata_to_opendataset/compare_side/"><img src="img/from_opendata_to_opendataset/compare_side.png" /></a>


Filter
Manually generate: `~rsp_dataset/cover.to_remove`

```
rsp subset --mode delete --dir ~/rsp_dataset/training/images --cover ~/rsp_dataset/cover.to_remove > /dev/null
rsp subset --mode delete --dir ~/rsp_dataset/training/labels --cover ~/rsp_dataset/cover.to_remove > /dev/null
rsp subset --mode delete --dir ~/rsp_dataset/validation/images --cover ~/rsp_dataset/cover.to_remove > /dev/null
rsp subset --mode delete --dir ~/rsp_dataset/validation/labels --cover ~/rsp_dataset/cover.to_remove > /dev/null
```


Train
```
rsp train --config config.toml --epochs 100 ~/rsp_dataset/pth_clean
```



<h1 align='center'>RoboSat.pink</h1>
<h2 align='center'>Semantic Segmentation ecosystem for GeoSpatial imagery</h2>

<p align=center>
  <img src="https://pbs.twimg.com/media/DpjonykWwAANpPr.jpg" alt="RoboSat.pink buildings segmentation from Imagery" />
</p>



Purposes:
---------
- DataSet Quality Analysis
- Change Detection highlighter
- Features extraction and completion


Main Features:
--------------
- Provides several command line tools, you can combine together to build your own workflow
- Follows geospatial standards to ease interoperability and data preparation 
- Build-in cutting edge Computer Vision model and loss implementations (and allows to replace by your owns)
- Support either RGB or multibands imagery (as multispectral or hyperspectral)
- Allows Data Fusion (from imagery or rasterized vectors)
- Web-UI tools to easily display, hilight or select results
- High performances, PyTorch based, and native multi GPUs support


News:
-----
- <a href='https://twitter.com/RobosatPink'>@RoboSatPink</a>


Documentation:
--------------

### Tutorials:
- <a href="./docs/from_opendata_to_opendataset.md">How to use plain OpenData to create a decent training OpenDataSet</a>
- <a href="./docs/extensibility_by_design.md">How to extend RoboSat.pink</a>

### Config file:
- <a href="./docs/config.md">`config.toml`</a> RoboSat.pink configuration file

### Tools:

- <a href="./docs/tools.md#rsp-cover">`rsp cover`</a> Generate a tiles covering, in csv format: X,Y,Z
- <a href="./docs/tools.md#rsp-download">`rsp download`</a> Downloads tiles from a remote server (XYZ, WMS, or TMS)
- <a href="./docs/tools.md#rsp-extract">`rsp extract`</a> Extracts GeoJSON features from OpenStreetMap .pbf
- <a href="./docs/tools.md#rsp-rasterize">`rsp rasterize`</a> Rasterize vector features (GeoJSON or PostGIS), to raster tiles
- <a href="./docs/tools.md#rsp-subset">`rsp subset`</a> Filter images in a slippy map dir using a csv tiles cover
- <a href="./docs/tools.md#rsp-tile">`rsp tile`</a> Tile a raster
- <a href="./docs/tools.md#rsp-train">`rsp train`</a> Trains a model on a dataset
- <a href="./docs/tools.md#rsp-export">`rsp export`</a> Export a model to ONNX or Torch JIT
- <a href="./docs/tools.md#rsp-predict">`rsp predict`</a> Predict masks, from given inputs and an already trained model
- <a href="./docs/tools.md#rsp-compare">`rsp compare`</a> Compute composite images and/or metrics to compare several XYZ dirs
- <a href="./docs/tools.md#rsp-vectorize">`rsp vectorize`</a> Extract simplified GeoJSON features from segmentation masks

### Presentations slides:
  - <a href="http://www.datapink.com/presentations/2018-pyparis.pdf">@PyParis 2018</a>
  - <a href="http://www.datapink.com/presentations/2019-fosdem.pdf">@FOSDEM 2019</a>

### Developpers tools:
- <a href="https://github.com/datapink/robosat.pink/blob/master/docs/makefile.md">```make```</a>


Install:
--------

### Using PIP:
```
pip3 install RoboSat.pink
```

### Using Conda, with a virtual env:
```
conda create -n robosat_pink python=3.6
conda activate robosat_pink
pip install robosat.pink
```

### Install from scratch:

Ubuntu 18.04:
```
sudo sh -c "apt update && apt install -y build-essential python3-pip"
pip3 install RoboSat.pink && export PATH=$PATH:~/.local/bin
```

CentOS 7:
```
sudo sh -c "yum -y update && yum install -y python36 wget && python3.6 -m ensurepip"
pip3 install --user RoboSat.pink
```

Add Nvidia GPU drivers:
```
wget http://us.download.nvidia.com/XFree86/Linux-x86_64/418.43/NVIDIA-Linux-x86_64-418.43.run 
sudo sh NVIDIA-Linux-x86_64-418.43.run -a -q --ui=none
```


### NOTAS: 
- Requires: Python 3.6 or later, and Nvidia GPU with at least 6Go RAM.
- To test RoboSat.pink install, launch in a terminal: `rsp -h`
- Upon your ```pip``` PATH setting, you may have to update it: ```export PATH=$PATH:.local/bin```
- To use instead the development version: ```pip3 install git+https://github.com/datapink/robosat.pink```


WorkFlows:
--------

### HelloWorld  ###
 

A minimal example:


```
# Configuration
wget -O config.toml https://raw.githubusercontent.com/datapink/robosat.pink/master/config.toml
export RSP_CONFIG=config.toml


# Data Preparation

rsp cover --type bbox 4.8,45.7,4.83,45.73 --zoom 18 cover

export WMS_URL='https://download.data.grandlyon.com/wms/grandlyon?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=Ortho2015_vue_ensemble_16cm_CC46&WIDTH=512&HEIGHT=512&CRS=EPSG:3857&BBOX={xmin},{ymin},{xmax},{ymax}&FORMAT=image/jpeg'
rsp download --type WMS "$WMS_URL" cover images

wget -nc -O lyon_roofprint.json 'https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=ms:fpc_fond_plan_communaut.fpctoit&VERSION=1.1.0&srsName=EPSG:4326&BBOX=4.79,45.69,4.84,45.74&outputFormat=application/json; subtype=geojson'
rsp rasterize --geojson lyon_roofprint.json cover labels

rsp cover --type dir images --splits 70,30 dataset/training/cover dataset/validation/cover
rsp subset --dir images --filter dataset/training/cover dataset/training/images
rsp subset --dir labels --filter dataset/training/cover dataset/training/labels
rsp subset --dir images --filter dataset/validation/cover dataset/validation/images
rsp subset --dir labels --filter dataset/validation/cover dataset/validation/labels


# Model Training and Prediction

rsp train --dataset dataset --epochs 5 models
rsp predict --checkpoint models/checkpoint-00005-of-00005.pth images masks
rsp compare --mode stack --labels labels --images images labels masks --masks masks compare

```

DataSet:
--------

- Training and validation datasets have to be tiled, using <a href="https://en.wikipedia.org/wiki/Tiled_web_map">XYZ tiles format</a>.
- A Dataset directory, so containing XYZ tiles, can be split as:
```
dataset
├── training
│   ├── images
│   └── labels
└── validation
    ├── images
    └── labels
```
- Tiles images formats could be either: JPEG, WEBP, GeoTIFF, PNG.
- Tiles labels are expected to be PNG with single band.
- Tools producing XYZ tiles directory as output, also allows to easily generate a web map client, for visual inspection.



### Data Preparation ###


Several ways to create your own training dataset, upon input data type:



<img alt="Data Preparation" src="https://raw.githubusercontent.com/datapink/robosat.pink/master/docs/img/readme/data_preparation.png" />

NOTA: several inputs connected to a single arrow point means a logical OR (e.g. WMS or XYZ or TMS).


### Training ###

<img alt="Training" src="https://raw.githubusercontent.com/datapink/robosat.pink/master/docs/img/readme/training.png" />




Architecture:
------------

<img alt="Stacks" src="https://raw.githubusercontent.com/datapink/robosat.pink/master/docs/img/readme/stacks.png" />
RoboSat.pink use cherry-picked Open Source libs among Deep Learning, Computer Vision and GIS stacks.




Related resources:
-----------------
- <a href="https://github.com/mapbox/robosat">Historical MapBox RoboSat github directory (not active anymore)</a>
- <a href="https://github.com/chrieke/awesome-satellite-imagery-datasets">Christoph Rieke's Awesome Satellite Imagery Datasets</a>
- <a href="https://github.com/mrgloom/awesome-semantic-segmentation">Mr Gloom's Awesome Semantic Segmentation</a>


Bibliography:
-------------

- <a href="https://arxiv.org/abs/1705.08790">The Lovász-Softmax loss: A tractable surrogate for the optimization of the IoU measure in neural networks</a>
- <a href="https://arxiv.org/abs/1505.04597">U-Net: Convolutional Networks for Biomedical Image Segmentation</a>
- <a href="https://arxiv.org/abs/1512.03385">Deep Residual Learning for Image Recognition</a>
- <a href="https://arxiv.org/pdf/1804.08024.pdf">Angiodysplasia Detection and Localization Using Deep
Convolutional Neural Networks</a>
- <a href="https://arxiv.org/abs/1806.00844">TernausNetV2: Fully Convolutional Network for Instance Segmentation</a>
- <a href="https://hal.archives-ouvertes.fr/hal-01523573/document">Joint Learning from Earth Observation and
OpenStreetMap Data to Get Faster Better Semantic Maps</a>



Contributions and Services:
---------------------------

- Pull Requests are welcome ! Feel free to send code...
  Don't hesitate either to initiate a prior discussion throught tickets on any implementation question.

- If you want to collaborate through code production and maintenance on a long term basis, please get in touch, co-edition with an ad hoc governance can be considered.

- If you want a new feature, but don't want to implement it, <a href="http://datapink.com">DataPink</a> provide core-dev services.

- Expertise and training on RoboSat.pink are also provided by <a href="http://datapink.com">DataPink</a>.

- And if you want to support the whole project, because it means for your own business, funding is also welcome.


Authors:
--------
- Daniel J. Hofmann <https://github.com/daniel-j-h>
- Olivier Courtin <https://github.com/ocourtin>

<a href="https://twitter.com/RobosatPink"><img src="https://img.shields.io/badge/Follow-%40RoboSatPink-ff69b4.svg" /></a>  <a href="https://gitter.im/RoboSatPink/community"><img src="https://img.shields.io/gitter/room/robosatpink/community.svg?color=ff69b4&style=popout" /></a> 

 

<h1 align='center'>RoboSat.pink</h1>
<h2 align='center'>Semantic Segmentation ecosystem for GeoSpatial imagery</h2>

<p align=center>
  <a href="http://www.datapink.tools/rsp/opendata_to_opendataset/compare_side_clean/"><img src="https://pbs.twimg.com/media/DpjonykWwAANpPr.jpg" alt="RoboSat.pink buildings segmentation from Imagery" /></a>
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
- High performances




 
Documentation:
--------------

### Tutorials:
- <a href="./docs/from_opendata_to_opendataset.md">How to use plain OpenData to create a decent training OpenDataSet</a>

### Config file:
- <a href="./docs/config.md">`config.toml`</a> RoboSat.pink configuration file

### Tools:

- <a href="https://github.com/datapink/robosat.pink/tree/master/docs/tools.md#rsp-cover">`rsp cover`</a> Generate a tiles covering, in csv format: X,Y,Z
- <a href="https://github.com/datapink/robosat.pink/tree/master/docs/tools.md#rsp-download">`rsp download`</a> Downloads tiles from a remote server (XYZ, WMS, or TMS)
- <a href="https://github.com/datapink/robosat.pink/tree/master/docs/tools.md#rsp-extract">`rsp extract`</a> Extracts GeoJSON features from OpenStreetMap .pbf
- <a href="https://github.com/datapink/robosat.pink/tree/master/docs/tools.md#rsp-rasterize">`rsp rasterize`</a> Rasterize vector features (GeoJSON or PostGIS), to raster tiles
- <a href="https://github.com/datapink/robosat.pink/tree/master/docs/tools.md#rsp-subset">`rsp subset`</a> Filter images in a slippy map dir using a csv tiles cover
- <a href="https://github.com/datapink/robosat.pink/tree/master/docs/tools.md#rsp-tile">`rsp tile`</a> Tile raster coverage
- <a href="https://github.com/datapink/robosat.pink/tree/master/docs/tools.md#rsp-train">`rsp train`</a> Trains a model on a dataset
- <a href="https://github.com/datapink/robosat.pink/tree/master/docs/tools.md#rsp-export">`rsp export`</a> Export a model to ONNX or Torch JIT
- <a href="https://github.com/datapink/robosat.pink/tree/master/docs/tools.md#rsp-predict">`rsp predict`</a> Predict masks, from given inputs and an already trained model
- <a href="https://github.com/datapink/robosat.pink/tree/master/docs/tools.md#rsp-compare">`rsp compare`</a> Compute composite images and/or metrics to compare several XYZ dirs
- <a href="https://github.com/datapink/robosat.pink/tree/master/docs/tools.md#rsp-vectorize">`rsp vectorize`</a> Extract simplified GeoJSON features from segmentation masks

### Presentations slides:
  - <a href="http://www.datapink.com/presentations/2018-pyparis.pdf">@PyParis 2018</a>
  - <a href="http://www.datapink.com/presentations/2019-fosdem.pdf">@FOSDEM 2019</a>


Installs:
--------

### With PIP:
```
pip3 install RoboSat.pink                                     # For latest stable version
```

or

```
pip3 install git+https://github.com/datapink/robosat.pink     # For current dev version
```

### With Conda, using a virtual env:
```
conda create -n robosat_pink python=3.6 && conda activate robosat_pink
pip install robosat.pink                                      # For latest stable version        
```

### With Ubuntu 18.04, from scratch:

```
sudo sh -c "apt update && apt install -y build-essential python3-pip"
pip3 install RoboSat.pink && export PATH=$PATH:~/.local/bin
pip3 install https://download.pytorch.org/whl/cu100/torch-1.0.1.post2-cp36-cp36m-linux_x86_64.whl
wget http://us.download.nvidia.com/XFree86/Linux-x86_64/418.43/NVIDIA-Linux-x86_64-418.43.run 
sudo sh NVIDIA-Linux-x86_64-418.43.run -a -q --ui=none
```

### With CentOS 7, from scratch:
```
sudo sh -c "yum -y update && yum install -y python36 wget && python3.6 -m ensurepip"
pip3 install --user RoboSat.pink
pip3 install --user https://download.pytorch.org/whl/cu100/torch-1.0.1.post2-cp36-cp36m-linux_x86_64.whl
wget http://us.download.nvidia.com/XFree86/Linux-x86_64/418.43/NVIDIA-Linux-x86_64-418.43.run 
sudo sh NVIDIA-Linux-x86_64-418.43.run -a -q --ui=none
```


### NOTAS: 
- Requires: Python 3.6 or later
- GPU is not strictly mandatory, but `rsp train` would be -that- slower without.
- To test RoboSat.pink install, launch in a terminal: `rsp -h`
- Upon your ```pip``` PATH setting, you may have to update it: ```export PATH=$PATH:.local/bin```
- PyTorch release published on PyPI is binded with CUDA 9. 
  For CUDA 10, grab a wheel <a href="https://pytorch.org/">from PyTorch web site</a>, e.g ```pip3 install https://download.pytorch.org/whl/cu100/torch-1.0.1.post2-cp36-cp36m-linux_x86_64.whl```



WorkFlows:
--------

### A Minimal example ###
 
 
 <img alt="Minimal Example" src="https://raw.githubusercontent.com/datapink/robosat.pink/master/docs/img/readme/minimal.png" />

 

1) Configuration:


```bash
echo '

[[channels]]
  name   = "images"
  bands = [1, 2, 3]

[[classes]]
  title = "Building"
  color = "deeppink"

[model]
  nn = "Albunet"
  da = "Strong"
  loss = "Lovasz"
  loader = "SemSegTiles"

' > ~/.rsp_config
```

2) Data Preparation:


```bash
rsp cover --bbox 4.8,45.7,4.83,45.73 --zoom 18 ds/cover
rsp download --type WMS 'https://download.data.grandlyon.com/wms/grandlyon?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=Ortho2015_vue_ensemble_16cm_CC46&WIDTH=512&HEIGHT=512&CRS=EPSG:3857&BBOX={xmin},{ymin},{xmax},{ymax}&FORMAT=image/jpeg' ds/cover ds/images

wget -nc -O ds/lyon_roofprint.json 'https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=ms:fpc_fond_plan_communaut.fpctoit&VERSION=1.1.0&srsName=EPSG:4326&BBOX=4.79,45.69,4.84,45.74&outputFormat=application/json; subtype=geojson'
rsp rasterize --geojson ds/lyon_roofprint.json --cover ds/cover ds/labels

rsp cover --dir ds/images --splits 70/20/10 ds/training/cover ds/validation/cover ds/prediction/cover
rsp subset --dir ds/images --cover ds/training/cover ds/training/images
rsp subset --dir ds/labels --cover ds/training/cover ds/training/labels
rsp subset --dir ds/images --cover ds/validation/cover ds/validation/images
rsp subset --dir ds/labels --cover ds/validation/cover ds/validation/labels
```

3) Model Training and Prediction:


```bash
rsp train  --epochs 5 --lr 0.000025 --bs 4 ds ds/models
rsp subset --dir ds/images --cover ds/prediction/cover ds/prediction/images
rsp predict --checkpoint ds/models/checkpoint-00005.pth ds/prediction ds/prediction/masks
rsp compare --images ds/prediction/images ds/prediction/masks --mode side ds/prediction/compare
```



DataSet:
-------

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
- Tiles images formats could be any able to be read by GDAL.
- Tiles labels are expected to be PNG with single band.
- Tools producing XYZ tiles directory, generate also a web map client, for visual inspection.



### Data Preparation ###


Several ways to create your own training dataset, upon input data type:



<img alt="Data Preparation" src="https://raw.githubusercontent.com/datapink/robosat.pink/master/docs/img/readme/data_preparation.png" />

NOTA: several inputs connected to a single arrow point means a logical OR (e.g. WMS or XYZ or TMS).




Architecture:
------------

<img alt="Stacks" src="https://raw.githubusercontent.com/datapink/robosat.pink/master/docs/img/readme/stacks.png" />
RoboSat.pink use cherry-picked Open Source libs among Deep Learning, Computer Vision and GIS stacks.




Related resources:
-----------------
- <a href="https://github.com/mapbox/robosat">Historical MapBox RoboSat github directory (not active anymore)</a>
- <a href="https://github.com/chrieke/awesome-satellite-imagery-datasets">Christoph Rieke's Awesome Satellite Imagery Datasets</a>
- <a href="https://landscape.satsummit.io/analysis/spectral-bands.html">Satellites in Global Development</a>


Bibliography:
-------------

- <a href="https://arxiv.org/abs/1505.04597">U-Net: Convolutional Networks for Biomedical Image Segmentation</a>
- <a href="https://arxiv.org/abs/1512.03385">Deep Residual Learning for Image Recognition</a>
- <a href="https://arxiv.org/pdf/1804.08024.pdf">Angiodysplasia Detection and Localization Using Deep
Convolutional Neural Networks</a>
- <a href="https://arxiv.org/abs/1806.00844">TernausNetV2: Fully Convolutional Network for Instance Segmentation</a>
- <a href="https://arxiv.org/abs/1705.08790">The Lovász-Softmax loss: A tractable surrogate for the optimization of the IoU measure in neural networks</a>
- <a href="https://hal.archives-ouvertes.fr/hal-01523573/document">Joint Learning from Earth Observation and
OpenStreetMap Data to Get Faster Better Semantic Maps</a>
- <a href="https://arxiv.org/abs/1809.06839">Albumentations: fast and flexible image augmentations</a>


Contributions and Services:
---------------------------

- Pull Requests are welcome ! Feel free to send code...
  Don't hesitate either to initiate a prior discussion via <a href="https://gitter.im/RoboSatPink/community">gitter</a> or ticket on any implementation question.
  And give also a look at <a href="https://github.com/datapink/robosat.pink/blob/master/docs/makefile.md">Makefile rules</a>.

- If you want to collaborate through code production and maintenance on a long term basis, please get in touch, co-edition with an ad hoc governance can be considered.

- If you want a new feature, but don't want to implement it, <a href="http://datapink.com">DataPink</a> provide core-dev services.

- Expertise and training on RoboSat.pink are also provided by <a href="http://datapink.com">DataPink</a>.

- And if you want to support the whole project, because it means for your own business, funding is also welcome.


Authors:
--------
- Daniel J. Hofmann <https://github.com/daniel-j-h>
- Olivier Courtin <https://github.com/ocourtin>

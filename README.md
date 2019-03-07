<h1 align='center'>RoboSat.pink</h1>
<h2 align='center'>Semantic Segmentation ecosystem for GeoSpatial Imagery</h2>


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
- Build-in cutting edge Computer Vision model and loss implementations (and allows to extend with your owns)
- Support either RGB or multibands imagery (as multispectral or hyperspectral)
- Allows data fusion (from imagery or rasterized vectors)
- Web-UI tools to easily display, filter or select results








Tutorials:
----------
- <a href="./docs/from_opendata_to_opendataset.md">From OpenData to OpenDataSet</a>
- <a href="./docs/extensibility_by_design.md">Using it as a FrameWork</a>

Presentations:
--------------
  - <a href="http://www.datapink.com/presentations/2018-pyparis.pdf">@PyParis 2018</a>
  - <a href="http://www.datapink.com/presentations/2019-fosdem.pdf">@FOSDEM 2019</a>


Install:
--------

```
pip3 install RoboSat.pink
```


Out of the box Ubuntu-server 18.04 full install:
```
sudo sh -c "apt update && apt install -y build-essential python3-pip"
sudo pip3 install RoboSat.pink
wget http://us.download.nvidia.com/XFree86/Linux-x86_64/418.43/NVIDIA-Linux-x86_64-418.43.run 
sudo sh NVIDIA-Linux-x86_64-418.43.run -a -q --ui=none
```


WorkFlows:
--------

### Data Preparation ###

- Training and validation datasets have to be tiled, using <a href="https://en.wikipedia.org/wiki/Tiled_web_map">XYZ tiles format</a>.
- A Dataset directory structure, must contains at least:
```
dataset
├── training
│   ├── images
│   └── labels
└── validation
    ├── images
    └── labels
```
- Following schema, show several paths to create your own training dataset from several kinds of input data. 
- And for information, an arrow sharing a same box anchor means a logical OR.


<img alt="Data Preparation" src="https://raw.githubusercontent.com/datapink/robosat.pink/master/docs/img/readme/data_preparation.png" />


### Training ###

<img alt="Training" src="https://raw.githubusercontent.com/datapink/robosat.pink/master/docs/img/readme/training.png" />




Stacks:
-------

RoboSat.pink use cherry-picked Open Source libs among Deep Learning, Computer Vision and GIS stacks.

<img alt="Stacks" src="https://raw.githubusercontent.com/datapink/robosat.pink/master/docs/img/readme/stacks.png" />




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

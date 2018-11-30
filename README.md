<h1 align='center'>RoboSat.pink</h1>
<h2 align='center'>Data Quality and feature extraction ecosystem, from Imagery</h2>


<p align=center>
  <img src="https://pbs.twimg.com/media/DpjonykWwAANpPr.jpg" alt="RoboSat pipeline extracting buildings from Imagery and Fusion" />
</p>




This repository is a DataPink flavor of RoboSat, including our latests developments.

Install:
-------

**1) Prerequisites:**
   - PyTorch >= 0.4 installed, with related Nvidia GPU drivers, CUDA and CUDNN libs.
   - At least one GPU, with RAM GPU >= 6Go (default batch_size settings is targeted to 11Go).
   - Libs with headers: libjpeg, libwebp, libbz2, zlib, libboost. 
     On a recent Ubuntu-server, could be done with:
 ```
     apt-get install build-essential libboost-python-dev zlib1g-dev libbz2-dev libjpeg-turbo8-dev libwebp-dev
 ```

 **2) Python libs Install:**
```
     python3 -m pip install requirements.txt
```
  NOTA: if you want to significantly increase performances switch from Pillow to <a href="https://github.com/uploadcare/pillow-simd">Pillow-simd</a>.


 **3) Deploy:**
  - Move the `rsp` command to a bin directory covered by your `PATH` (or update your `PATH`)
  - Move the robosat_pink dir to somewhere covered by your `PYTHONPATH` (or update your `PYTHONPATH`)





WorkFlows:
--------
![Data Preparation Workflow](docs/img/data_preparation.png)
![Training Workflow](docs/img/training.png)      



Related resources:
-----------------

- <a href="http://www.datapink.com/presentations/2018-pyparis.pdf">Robosat slides @PyParis 2018</a>
- <a href="https://github.com/mapbox/robosat">MapBox RoboSat github directory</a>
- <a href="https://github.com/chrieke/awesome-satellite-imagery-datasets">Christoph Rieke's Awesome Satellite Imagery Datasets</a>

Bibliography:
-------------

- <a href="http://www.cs.umanitoba.ca/~ywang/papers/isvc16.pdf">Optimizing IoU in Deep
Neural Networks for Image Segmentation</a>
- <a href="http://www.cs.toronto.edu/~wenjie/papers/iccv17/mattyus_etal_iccv17.pdf">DeepRoadMapper: Extracting Road Topology from Aerial Images</a>
- <a href="https://arxiv.org/abs/1705.08790">The Lovász-Softmax loss: A tractable surrogate for the optimization of the IoU measure in neural networks</a>
- <a href="https://arxiv.org/abs/1505.04597">U-Net: Convolutional Networks for Biomedical Image Segmentation</a>
- <a href="https://arxiv.org/abs/1512.03385">Deep Residual Learning for Image Recognition</a>
- <a href="https://arxiv.org/pdf/1804.08024.pdf">Angiodysplasia Detection and Localization Using Deep
Convolutional Neural Networks</a>
- <a href="https://arxiv.org/abs/1806.00844">TernausNetV2: Fully Convolutional Network for Instance Segmentation</a>
- <a href="https://hal.archives-ouvertes.fr/hal-01523573/document">Joint Learning from Earth Observation and
OpenStreetMap Data to Get Faster Better Semantic Maps</a>
- <a href="https://arxiv.org/abs/1712.02616">In-Place Activated BatchNorm for Memory-Optimized Training of DNNs</a>

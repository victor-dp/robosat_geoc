# How to extend RoboSat.pink: 

RoboSat.pink extensibility design allows you to custom it easily to your specifics needs.



## Use an alternate Web UI Templates ##
RoboSat.pink tools outputing XYZ tiles, can generate, on demand, a Web UI, with `--web_ui` parameter.
To switch to your own HTML template, just add `--web_ui_template` followed by your own template path.

Special values are substitued, if presents, in a template:
 - `{{base_url}}` XYZ directory base url, containing tiles. 
 - `{{ext}}` file extension to tiles image.
 - `{{zoom}}` z level from tiles coverage.
 - `{{center}}` lon, lat coordinates from center point of coverage. 
 - `{{tiles}}` JSON selected tiles list, if any. 


A minimal Leaflet based template example:
```
<!DOCTYPE html>
<html>
<head>
  <title>RoboSat.pink Leaflet WebUI</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.3.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.3.4/dist/leaflet.js"></script>
</head>
<body>
  <div id="mapid" style="width:100%; height:100vh;"></div>
  <script>
   var m = L.map("mapid").setView({{center}}, {{zoom}});
   L.tileLayer("{{base_url}}/{z}/{x}/{y}.{{ext}}").addTo(m);
  </script>
</body>
</html>
```


## Use an alternate OSM type extractor ##
To allows `rsp extract` to handle new OSM types:
- Retrieve RoboSat.pink code from GitHub and launch `make install`
- Create a `yourtypename.py` file containing at least a `yourtypenameHandler` class, with `__init__`, `ways` and `save` methods.
- This file must be located in `robosat_pink.osm` package:

```
└── robosat_pink
    └── osm
         └──yourtypename.py 
```


A simple OSM `leisure:park` extractor example, callable with `rsp extract --type park`:

```
import osmium
import geojson
import shapely.geometry


class ParkHandler(osmium.SimpleHandler):

    def __init__(self):
        super().__init__()
        self.features = []

    def way(self, w):
        if "leisure" not in w.tags or w.tags["leisure"] != "park":
            return
            
        if not w.is_closed() or len(w.nodes) < 4:
            return

        geometry = geojson.Polygon([[(n.lon, n.lat) for n in w.nodes]])
        shape = shapely.geometry.shape(geometry)

        if shape.is_valid:
            feature = geojson.Feature(geometry=geometry)
            self.features.append(feature)

    def save(self, out):
        with open(out, "w") as fp:
            geojson.dump(geojson.FeatureCollection(self.features), fp)
```




## Use an alternate Loss function ##

To allows `rsp train` to use a loss function of your own:
- Retrieve RoboSat.pink code from GitHub and launch `make install`
- Create a yourlossname.py file containing at least a class, with `__init__` and `forward` methods.
- This file must be located in `robosat_pink.losses` package:
```
└── robosat_pink
    └── losses
         └──yourlossname.py 
```

As an example, a MIoU loss, callable with `rsp train --loss miou`:


```
import torch

class Miou(torch.nn.Module):
    """mIoU Loss. cf http://www.cs.umanitoba.ca/~ywang/papers/isvc16.pdf"""

    def __init__(self):
        super().__init__()

    def forward(self, inputs, targets):

        N, C, H, W = inputs.size()

        softs = torch.nn.functional.softmax(inputs, dim=1).permute(1, 0, 2, 3)
        masks = torch.zeros(N, C, H, W).to(targets.device).scatter_(1, targets.view(N, 1, H, W), 1).permute(1, 0, 2, 3)

        inters = softs * masks
        unions = (softs + masks) - (softs * masks)
        mIoU = 1. - (inters.view(C, N, -1).sum(2) / unions.view(C, N, -1).sum(2)).mean()

        return mIoU
```

Nota: If your loss computation is not auto-differentiable by PyTorch, a related `backward` method, will be needed too.


## Use an alternate Neural Network Model ##
To allows `rsp train` and `rsp predict` to use a model of your own:
- Retrieve RoboSat.pink code from GitHub and launch `make install`
- Create a `yourmodelname.py` file containing at least a `Model_name` class, with `__init__` and `forward` methods.
- This file must be located in `robosat_pink.models` package:
```
└── robosat_pink
    └── models
         └──yourmodelname.py 
```
- Then, to use it, with `rsp train` and `rsp predict` either:
  - update config file value: `["model"]["name"]`
  - use `--model` parameter

# How to extend RoboSat.pink: 

RoboSat.pink extensibility design allows you to custom it easily to your specifics needs.


## Use an alternate Neural Network Model ##
To allows `rsp train` and `rsp predict` to use a model of your own:
- In your extension directory (or an empty dir) create a sub dir `models`, and inside it a file: `your_model_name.py`
- The file must contains at least a `Model_name` class, with `__init__` and `forward` methods.
- Either update config file value: `["model"]["name"]` or use `rsp train` with related `--model` parameter
- Call either `rsp train` or `rsp predict` with `--ext_path` pointing to your extension directory.


## Use an alternate Loss function ##
To allows `rsp train` to use a Loss function of your own:
- In your extension directory (or an empty dir) create a sub dir `losses`, and inside it a file: `your_loss_name.py`
- This file must contains at least a `Loss_name` class, with `__init__` and `forward` methods.
- If your loss computation is not auto-differentiable by PyTorch, a related `backward` method, will be needed too.
- Either update config file value: `["model"]["loss"]` or use `rsp train` with related `--loss` parameter
- Call `rsp train` with `--ext_path` pointing to your extension directory.


## Use an alternate OSM type extractor ##
To allows `rsp extract` to handle new OSM types:
- In your extension directory (or an empty dir) create a sub dir `osm`, and inside it a file: `your_type_name.py`
- This file must contains at least a `type_nameHandler` class, with `__init__`, `ways` and `save` methods.
- Call `rsp extract` with `--ext_path` pointing to your extension directory, and the new `--type` value.

A simple OSM leisure:park extractor example:

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

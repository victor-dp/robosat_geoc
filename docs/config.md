## config.toml
```
# RoboSat.pink Configuration

[dataset]

  # Optional PostgreSQL Database connection, using psycopg2 syntax (could be use by rasterize tool)
  pg_dsn = "host=127.0.0.1 dbname=rsp user=postgres"


# Input channels configuration
# You can, add several channels blocks to compose your input Tensor. Order is meaningful.
#
# sub:		dataset subdirectory name
# bands:	bands to keep from sub source. Order is meaningful
# mean:		bands mean value [default, if model pretrained: [0.485, 0.456, 0.406] ]
# std:		bands std value  [default, if model pretrained: [0.229, 0.224, 0.225] ]

[[channels]]
  name   = "images"
  bands = [1, 2, 3]


# Output Classes configuration
# Nota: available colors are either CSS3 colors names or #RRGGBB hexadecimal representation.
# Nota: only support binary classification for now.

[[classes]]
  title = "background"
  color = "white"

[[classes]]
  title = "Building"
  color = "deeppink"



[model]
  # Model name
  name = "Albunet"

  # Pretrained on ImageNet
  pretrained = true

  # Loss function name
  loss = "Lovasz"
  
  # Batch size for training
  batch_size = 4

  # Learning rate for the optimizer
  lr = 0.000025

  # Model internal input tile size
  tile_size = 512

  # Dataset loader name
  loader = "SemSegTiles"

  # Kind of data augmentation to apply while training
  da = "GeoSpatial"

  # Data Augmentation probability
  dap = 0.75
```

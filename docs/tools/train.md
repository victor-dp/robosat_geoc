# rsp train
```
usage: rsp train [-h] --config CONFIG [--dataset DATASET] [--epochs EPOCHS]
                 [--batch_size BATCH_SIZE] [--model MODEL] [--loss LOSS]
                 [--lr LR] [--resume] [--checkpoint CHECKPOINT]
                 [--ext_path EXT_PATH] [--workers WORKERS]
                 out

optional arguments:
 -h, --help               show this help message and exit

Hyper Parameters:
 --config CONFIG          path to configuration file [required]
 --dataset DATASET        if set, override dataset path value from config file
 --epochs EPOCHS          if set, override epochs value from config file
 --batch_size BATCH_SIZE  if set, override batch_size value from config file
 --model MODEL            if set, override model name from config file
 --loss LOSS              if set, override model loss from config file
 --lr LR                  if set, override learning rate value from config file

Output:
 out                      output directory path to save checkpoint .pth files and logs [required]

Model Training:
 --resume                 resume model training, if set imply to provide a checkpoint
 --checkpoint CHECKPOINT  path to a model checkpoint. To fine tune, or resume training if setted
 --ext_path EXT_PATH      path to user's extension modules dir. To use alternate models or losses

Performances:
 --workers WORKERS        number pre-processing images workers [default: 0]
```

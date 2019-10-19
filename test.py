from datetime import datetime
import time
import json
from robosat_pink.geoc import RSPtrain
from robosat_pink.geoc import RSPpredict


def train(extent, dataPath, dsPath, map="tdt", auto_delete=False):
    return RSPtrain.main(extent, dataPath, dsPath, map, auto_delete)


def predict(extent, dataPath, dsPath, map="tdt", auto_delete=False):
    return RSPpredict.main(extent, dataPath, dsPath, map, auto_delete)


if __name__ == "__main__":
    # config.toml & checkpoint.pth data directory
    dataPath = "data"

    # training dataset directory
    startTime = datetime.now()
    ts = time.time()
    dsPath = "ds/train_" + str(ts)

    # map extent for training or predicting
    extent = "116.28993598937751,39.94242576681765,116.2948812791335,39.9454852957874"
    # extent = "116.3094,39.9313,116.3114,39.9323"

    # trainging
    train(extent, dataPath, dsPath)

    # predicting
    # print(predict(extent, dataPath, dsPath))

    endTime = datetime.now()
    timeSpend = (endTime-startTime).seconds
    print("Training or Predicting DONE！All spends：", timeSpend, "seconds！")

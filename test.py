from datetime import datetime
import time
import json
from robosat_pink.geoc import RSPtrain
from robosat_pink.geoc import RSPpredict


def train(extent, dataPath, dsPath, pthPath, map="tdt", auto_delete=False):
    return RSPtrain.main(extent, dataPath, dsPath, pthPath, map, auto_delete)


def predict(extent, dataPath, dsPath, pthPath, map="tdt", auto_delete=False):
    return RSPpredict.main(extent, dataPath, dsPath, pthPath, map, auto_delete)


if __name__ == "__main__":
    # config.toml & checkpoint.pth data directory
    dataPath = "data"

    # training dataset directory
    startTime = datetime.now()
    ts = time.time()
    dsPath = "ds/train_" + str(ts)

    # training or predict checkpoint.pth
    checkpointPth = dataPath + "/model/checkpoint-00010.pth"

    # map extent for training or predicting
    extent = "116.30356389344286,39.94539352737931,116.31383138955249,39.951225040754366"
    # extent = "116.3094,39.9313,116.3114,39.9323"

    result = ""
    # trainging
    result = train(extent, dataPath, dsPath, checkpointPth)

    # predicting
    # result = predict(extent, dataPath, dsPath,checkpointPth)

    print(result)

    endTime = datetime.now()
    timeSpend = (endTime-startTime).seconds
    print("Training or Predicting DONE！All spends：", timeSpend, "seconds！")

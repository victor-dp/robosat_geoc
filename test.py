from datetime import datetime
import time
import json
from robosat_pink.geoc import RSPtrain, RSPpredict, utils


def train(extent, dataPath, dsPath, pthNum, epochs=10, map="tdt", auto_delete=False):
    return RSPtrain.main(extent, dataPath, dsPath, pthNum, epochs, map, auto_delete)


def predict(extent, dataPath, dsPath, pthNum, map="tdt", auto_delete=False):
    return RSPpredict.main(extent, dataPath, dsPath, pthNum, map, auto_delete)


if __name__ == "__main__":
    # config.toml & checkpoint.pth data directory
    dataPath = "data"

    # training dataset directory
    startTime = datetime.now()
    ts = time.time()

    # training or predict checkpoint.pth number
    pthNum = utils.getLastPth(dataPath)

    # map extent for training or predicting
    extent = "116.27696226366453,39.91039327747811,116.2885978117277,39.91874087523394"
    # extent = "116.3094,39.9313,116.3114,39.9323"

    result = ""
    # trainging
    # result = train(extent, dataPath, "ds/train_" + str(ts), pthNum, 1)

    # predicting
    result = predict(extent, dataPath, "ds/predict_" + str(ts), pthNum)

    print(result)

    endTime = datetime.now()
    timeSpend = (endTime-startTime).seconds
    print("Training or Predicting DONE！All spends：", timeSpend, "seconds！")

import RSPtrain
import RSPpredict
import json


def train(extent):
    return RSPtrain.main(extent, map="tdt", auto_delete=False)


def predict(extent):
    return RSPpredict.main(extent, map="tdt", auto_delete=False)


if __name__ == "__main__":
    extent = "116.30952537059784,39.93146309816143,116.31227731704712,39.933264789366056"

    train(extent)

    predict(extent)

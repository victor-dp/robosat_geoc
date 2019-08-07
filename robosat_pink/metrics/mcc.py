import math
from robosat_pink.metrics.core import confusion


def get(label, predicted, config=None):

    tn, fn, fp, tp = confusion(label, predicted)

    try:
        mcc = (tp * tn - fp * fn) / math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    except ZeroDivisionError:
        mcc = 0.0

    return mcc

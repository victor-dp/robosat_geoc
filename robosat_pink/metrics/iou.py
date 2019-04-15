from robosat_pink.metrics.core import confusion


def get(label, predicted, config=None):

    tn, fn, fp, tp = confusion(label, predicted)

    try:
        iou = tp / (tp + fn + fp)
    except ZeroDivisionError:
        iou = float("NaN")

    return iou

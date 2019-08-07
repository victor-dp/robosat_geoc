from robosat_pink.metrics.core import confusion


def get(label, predicted, config=None):

    tn, fn, fp, tp = confusion(label, predicted)

    try:
        iou = tp / (tp + fn + fp)
    except ZeroDivisionError:
        iou = 1.0

    return iou

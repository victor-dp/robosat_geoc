import torch
from robosat_pink.core import load_module


class Metrics:
    def __init__(self, metrics, config=None):
        self.config = config
        self.metrics = {metric: 0.0 for metric in metrics}
        self.modules = {metric: load_module("robosat_pink.metrics." + metric) for metric in metrics}
        self.n = 0

    def add(self, mask, output):
        assert self.modules
        assert self.metrics
        self.n += 1
        for metric, module in self.modules.items():
            m = module.get(mask, output, self.config)
            m = m if m == m else 1.0
            self.metrics[metric] += m

    def get(self):
        assert self.metrics
        assert self.n
        return {metric: value / self.n for metric, value in self.metrics.items()}


def confusion(predicted, label):
    confusion = predicted.view(-1).float() / label.view(-1).float()

    tn = torch.sum(torch.isnan(confusion)).item()
    fn = torch.sum(confusion == float("inf")).item()
    fp = torch.sum(confusion == 0).item()
    tp = torch.sum(confusion == 1).item()

    return tn, fn, fp, tp

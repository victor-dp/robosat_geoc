import os
import sys

import torch
import torch.backends.cudnn
from torch.optim import Adam
from torch.utils.data import DataLoader
from torchvision.transforms import Normalize

from tqdm import tqdm

from importlib import import_module

from robosat_pink.transforms import (
    JointCompose,
    JointResize,
    JointTransform,
    JointRandomFlipOrRotate,
    ImageToTensor,
    MaskToTensor,
)
from robosat_pink.metrics import Metrics
from robosat_pink.config import load_config, check_model, check_channels, check_classes, check_dataset
from robosat_pink.logs import Logs


def add_parser(subparser, formatter_class):
    parser = subparser.add_parser("train", help="Trains a model on a dataset", formatter_class=formatter_class)

    parser.add_argument("--config", type=str, help="path to config file [required if RSP_CONFIG env var is not set]")

    data = parser.add_argument_group("Dataset")
    data.add_argument("--dataset", type=str, help="training dataset path [if set override config file value]")
    data.add_argument("--loader", type=str, help="dataset loader name [if set override config file value]")
    data.add_argument("--workers", type=int, help="number of pre-processing images workers [default: GPUs x 2]")

    hp = parser.add_argument_group("Hyper Parameters [if set override config file value]")
    hp.add_argument("--batch_size", type=int, help="batch_size")
    hp.add_argument("--lr", type=float, help="learning rate")
    hp.add_argument("--model", type=str, help="model name")
    hp.add_argument("--loss", type=str, help="model loss")

    mt = parser.add_argument_group("Model Training")
    mt.add_argument("--epochs", type=int, default=10, help="number of epochs to train [default 10]")
    mt.add_argument("--resume", action="store_true", help="resume model training, if set imply to provide a checkpoint")
    mt.add_argument("--checkpoint", type=str, help="path to a model checkpoint. To fine tune or resume a training")

    out = parser.add_argument_group("Output")
    out.add_argument("out", type=str, help="output directory path to save checkpoint .pth files and logs [required]")

    parser.set_defaults(func=main)


def main(args):
    config = load_config(args.config)
    args.out = os.path.expanduser(args.out)
    args.workers = torch.cuda.device_count() * 2 if torch.device("cuda") and not args.workers else args.workers
    config["dataset"]["path"] = args.dataset if args.dataset else config["dataset"]["path"]
    config["model"]["loader"] = args.loader if args.loader else config["model"]["loader"]
    config["model"]["lr"] = args.lr if args.lr else config["model"]["lr"]
    config["model"]["batch_size"] = args.batch_size if args.batch_size else config["model"]["batch_size"]
    config["model"]["name"] = args.model if args.model else config["model"]["name"]
    config["model"]["loss"] = args.loss if args.loss else config["model"]["loss"]
    check_dataset(config)
    check_classes(config)
    check_channels(config)
    check_model(config)

    log = Logs(os.path.join(args.out, "log"))

    if torch.cuda.is_available():
        log.log("RoboSat.pink - training on {} GPUs, with {} workers".format(torch.cuda.device_count(), args.workers))
        log.log("(Torch:{} Cuda:{} CudNN:{})".format(torch.__version__, torch.version.cuda, torch.backends.cudnn.version()))
        device = torch.device("cuda")
        torch.backends.cudnn.benchmark = True
    else:
        log.log("RoboSat.pink - training on CPU, with {} workers - (Torch:{})".format(args.workers, torch.__version__))
        log.log("WARNING: Are you really sure sure about not training on GPU ?")
        device = torch.device("cpu")

    try:
        model_module = import_module("robosat_pink.models.{}".format(config["model"]["name"].lower()))
        net = getattr(model_module, config["model"]["name"])(config).to(device)
        net = torch.nn.DataParallel(net)
    except:
        sys.exit("ERROR: Unable to load {} model".format(config["model"]["name"]))

    try:
        optimizer = Adam(net.parameters(), lr=config["model"]["lr"])
    except:
        sys.exit("ERROR: Unable to load optimizer")

    resume = 0
    if args.checkpoint:

        try:

            def map_location(storage, _):  # FIXME
                return storage.cuda() if torch.cuda.is_available() else storage.cpu()

            chkpt = torch.load(os.path.expanduser(args.checkpoint), map_location=map_location)
            net.load_state_dict(chkpt["state_dict"])

            log.log("Using checkpoint: {}".format(args.checkpoint))

            if args.resume:
                optimizer.load_state_dict(chkpt["optimizer"])
                resume = chkpt["epoch"]
                if resume >= args.epochs:
                    sys.exit(
                        "ERROR: Epoch {} set in {} already reached by the checkpoint provided".format(
                            config["model"]["epochs"], args.config
                        )
                    )
        except:
            sys.exit("ERROR: Unable to load {} checkpoint".format(args.checkpoint))

    try:
        loss_module = import_module("robosat_pink.losses.{}".format(config["model"]["loss"].lower()))
        criterion = getattr(loss_module, config["model"]["loss"])().to(device)
    except:
        sys.exit("ERROR: Unable to load {} loss".format(config["model"]["loss"]))

    try:
        train_loader, val_loader = get_dataset_loaders(config["dataset"]["path"], config, args.workers)
    except:
        sys.exit("ERROR: Unable to create data loaders")

    log.log("--- Input tensor from Dataset: {} ---".format(config["dataset"]["path"]))
    num_channel = 1
    for channel in config["channels"]:
        for band in channel["bands"]:
            log.log("Channel {}:\t\t {}[band: {}]".format(num_channel, channel["name"], band))
            num_channel += 1

    log.log("--- Hyper Parameters ---")
    for hp in config["model"]:
        log.log("{}{}".format(hp.ljust(25, " "), config["model"][hp]))

    for epoch in range(resume, args.epochs):
        log.log("---")
        log.log("Epoch: {}/{}".format(epoch + 1, args.epochs))

        train_hist = train(train_loader, config, device, net, optimizer, criterion)
        log.log(
            "Train    loss: {:.4f}, mIoU: {:.3f}, {} IoU: {:.3f}, MCC: {:.3f}".format(
                train_hist["loss"],
                train_hist["miou"],
                config["classes"][1]["title"],
                train_hist["fg_iou"],
                train_hist["mcc"],
            )
        )

        try:
            val_hist = validate(val_loader, config, device, net, criterion)
        except:
            sys.exit("ERROR: train error")
        log.log(
            "Validate loss: {:.4f}, mIoU: {:.3f}, {} IoU: {:.3f}, MCC: {:.3f}".format(
                val_hist["loss"], val_hist["miou"], config["classes"][1]["title"], val_hist["fg_iou"], val_hist["mcc"]
            )
        )

        try:
            states = {"epoch": epoch + 1, "state_dict": net.state_dict(), "optimizer": optimizer.state_dict()}
            checkpoint_path = os.path.join(args.out, "checkpoint-{:05d}-of-{:05d}.pth".format(epoch + 1, args.epochs))
            torch.save(states, checkpoint_path)
        except:
            sys.exit("ERROR: Unable to save checkpoint {}".format(checkpoint_path))


def train(loader, config, device, net, optimizer, criterion):
    num_samples = 0
    running_loss = 0

    metrics = Metrics()

    net.train()

    for images, masks, tiles in tqdm(loader, desc="Train", unit="batch", ascii=True):
        images = images.to(device)
        masks = masks.to(device)

        assert images.size()[2:] == masks.size()[1:], "resolutions for images and masks are in sync"

        num_samples += int(images.size(0))

        optimizer.zero_grad()
        outputs = net(images)

        assert outputs.size()[2:] == masks.size()[1:], "resolutions for predictions and masks are in sync"
        assert outputs.size()[1] == len(config["classes"]), "classes for predictions and dataset are in sync"

        loss = criterion(outputs, masks, config)
        loss.backward()

        optimizer.step()

        running_loss += loss.item()

        for mask, output in zip(masks, outputs):
            prediction = output.detach()
            metrics.add(mask, prediction)

    assert num_samples > 0, "dataset contains training images and labels"

    return {
        "loss": running_loss / num_samples,
        "miou": metrics.get_miou(),
        "fg_iou": metrics.get_fg_iou(),
        "mcc": metrics.get_mcc(),
    }


def validate(loader, config, device, net, criterion):

    num_samples = 0
    running_loss = 0

    metrics = Metrics()
    net.eval()

    with torch.no_grad():
        for images, masks, tiles in tqdm(loader, desc="Validate", unit="batch", ascii=True):
            images = images.to(device)
            masks = masks.to(device)

            assert images.size()[2:] == masks.size()[1:], "resolutions for images and masks are in sync"

            num_samples += int(images.size(0))
            outputs = net(images)

            assert outputs.size()[2:] == masks.size()[1:], "resolutions for predictions and masks are in sync"
            assert outputs.size()[1] == len(config["classes"]), "classes for predictions and dataset are in sync"

            loss = criterion(outputs, masks, config)
            running_loss += loss.item()

            for mask, output in zip(masks, outputs):
                metrics.add(mask, output)

    assert num_samples > 0, "dataset contains validation images and labels"

    return {
        "loss": running_loss / num_samples,
        "miou": metrics.get_miou(),
        "fg_iou": metrics.get_fg_iou(),
        "mcc": metrics.get_mcc(),
    }


def get_dataset_loaders(path, config, num_workers):

    std = []
    mean = []
    for channel in config["channels"]:
        std.extend(channel["std"])
        mean.extend(channel["mean"])

    transform = JointCompose(
        [
            JointResize(config["model"]["tile_size"]),
            JointRandomFlipOrRotate(config["model"]["data_augmentation"]),
            JointTransform(ImageToTensor(), MaskToTensor()),
            JointTransform(Normalize(mean=mean, std=std), None),
        ]
    )

    loader = import_module("robosat_pink.loaders.{}".format(config["model"]["loader"].lower()))
    loader_train = getattr(loader, config["model"]["loader"])(config, os.path.join(path, "training"), transform, "train")
    loader_val = getattr(loader, config["model"]["loader"])(config, os.path.join(path, "validation"), transform, "train")

    batch_size = config["model"]["batch_size"]
    train_loader = DataLoader(loader_train, batch_size=batch_size, shuffle=True, drop_last=True, num_workers=num_workers)
    val_loader = DataLoader(loader_val, batch_size=batch_size, shuffle=False, drop_last=True, num_workers=num_workers)

    return train_loader, val_loader

""" Dictionary-based configuration with a TOML-based on-disk representation. Cf: https://github.com/toml-lang/toml """

import os
import sys
import toml

import robosat_pink.colors as colors


def load_config(path):
    """Loads a dictionary from configuration file."""

    try:
        path = os.environ["RSP_CONFIG"] if not path else path
    except:
        sys.exit("CONFIG ERROR: Either RSP_CONFIG env var or --config parameter, is required.")

    try:
        config = toml.load(os.path.expanduser(path))
    except:
        sys.exit("CONFIG ERROR: Unable to load config file, check both path and syntax.")

    return config


def check_dataset(config):
    """Check if config file classes subpart is consistent. Exit on error if not."""

    try:
        assert os.path.isdir(os.path.expanduser(config["dataset"]["path"]))
    except:
        sys.exit("CONFIG ERROR: Missing or invalid dataset.path value.")

    check_channels(config)
    # TODO: check consistency on images/labels (including cover, tile size, bands and no empty tile)


def check_channels(config):
    if "channels" not in config.keys():
        sys.exit("CONFIG ERROR: At least one channel is mandatory.")

    for channel in config["channels"]:
        if not (len(channel["bands"]) == len(channel["mean"]) == len(channel["std"])):
            sys.exit("CONFIG ERROR: Inconsistent channel bands, mean or std lenght in config file")


def check_classes(config):
    """Check if config file classes subpart is consistent. Exit on error if not."""

    if "classes" not in config.keys():
        sys.exit("CONFIG ERROR: At least one class is mandatory.")

    if len(config["classes"]) > 2:
        sys.exit("CONFIG ERROR: For now, only binary classifications are available.")

    for classe in config["classes"]:
        if "title" not in classe.keys() or not len(classe["title"]):
            sys.exit("CONFIG ERROR: Missing or empty classes.title value.")

        if "color" not in classe.keys() or not colors.check_color(classe["color"]):
            sys.exit("CONFIG ERROR: Missing or invalid classes.color value.")


def check_model(config):

    hps = {
        "name": "str",
        "encoder": "str",
        "pretrained": "bool",
        "loss": "str",
        "batch_size": "int",
        "tile_size": "int",
        "lr": "float",
        "data_augmentation": "float",
        "decay": "float",
    }

    for hp in hps:
        if hp not in config["model"].keys() or type(config["model"][hp]).__name__ != hps[hp]:
            sys.exit("CONFIG ERROR: Missing or invalid model.{} value.".format(hp))

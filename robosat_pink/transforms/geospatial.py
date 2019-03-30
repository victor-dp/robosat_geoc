from albumentations import (
    Compose,
    Resize,
    IAAAdditiveGaussianNoise,
    GaussNoise,
    OneOf,
    Flip,
    Transpose,
    MotionBlur,
    Blur,
    ShiftScaleRotate,
    IAASharpen,
    IAAEmboss,
    RandomBrightnessContrast,
    MedianBlur,
    HueSaturationValue,
)


def transform(config, image, mask):

    try:
        p = config["model"]["dap"]
    except:
        p = 1

    assert 0 <= p <= 1
    assert config["model"]["tile_size"]

    return Compose(
        [
            Resize(config["model"]["tile_size"], config["model"]["tile_size"]),
            Flip(),
            Transpose(),
            OneOf([IAAAdditiveGaussianNoise(), GaussNoise()], p=0.2),
            OneOf([MotionBlur(p=0.2), MedianBlur(blur_limit=3, p=0.1), Blur(blur_limit=3, p=0.1)], p=0.2),
            ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.2, rotate_limit=45, p=0.2),
            OneOf([IAASharpen(), IAAEmboss(), RandomBrightnessContrast()], p=0.3),
            HueSaturationValue(p=0.3),
        ]
    )(image=image, mask=mask, p=p)

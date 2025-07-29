# tiff-tf-loader

`tiff_image_dataset_from_directory()` is a utility that lets you load `.tif` images into TensorFlow `tf.data.Dataset` pipelines, similar to `image_dataset_from_directory()` — but using `rasterio` under the hood.

## Installation

```bash
pip install tiff-tf-loader

Usage

from tiff_tf_loader import tiff_image_dataset_from_directory

train_ds = tiff_image_dataset_from_directory(
    "/path/to/data",
    image_size=(128, 128),
    batch_size=32,
    label_mode="categorical",
    validation_split=0.2,
    subset="training",
    seed=42
)

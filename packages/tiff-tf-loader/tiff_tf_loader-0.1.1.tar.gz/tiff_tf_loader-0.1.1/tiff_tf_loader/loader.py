import tensorflow as tf
import numpy as np
import rasterio
from pathlib import Path
from sklearn.model_selection import train_test_split

def tiff_image_dataset_from_directory(
    directory,
    image_size=(128, 128),
    batch_size=32,
    label_mode='categorical',
    validation_split=None,
    subset=None,
    seed=None,
):
    class_dirs = sorted([p for p in Path(directory).iterdir() if p.is_dir()])
    class_names = [p.name for p in class_dirs]

    filepaths, labels = [], []
    for label_idx, class_dir in enumerate(class_dirs):
        for f in class_dir.glob('*.tif'):
            filepaths.append(str(f))
            labels.append(label_idx)

    if validation_split:
        train_paths, val_paths, train_labels, val_labels = train_test_split(
            filepaths, labels, test_size=validation_split, stratify=labels, random_state=seed
        )
        if subset == 'training':
            filepaths, labels = train_paths, train_labels
        elif subset == 'validation':
            filepaths, labels = val_paths, val_labels
        else:
            raise ValueError("subset must be 'training' or 'validation'")

    def load_image(path, label):
        def _read_tif(p):
            with rasterio.open(p.decode()) as src:
                img = src.read([1, 2, 3])
                img = np.transpose(img, (1, 2, 0))
                img = tf.image.resize(img, image_size) / 255.0
                return img.numpy().astype(np.float32)
        image = tf.numpy_function(_read_tif, [path], tf.float32)
        image.set_shape((*image_size, 3))

        if label_mode == 'categorical':
            label = tf.one_hot(label, depth=len(class_names))
            label.set_shape((len(class_names),))
        elif label_mode == 'int':
            label = tf.cast(label, tf.int32)
        else:
            raise ValueError("Unsupported label_mode")
        return image, label

    ds = tf.data.Dataset.from_tensor_slices((filepaths, labels))
    ds = ds.shuffle(len(filepaths), seed=seed)
    ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds

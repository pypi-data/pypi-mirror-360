import tensorflow as tf
from sklearn import metrics
import matplotlib.pyplot as plt
import shutil
import random
import os
import numpy as np
from tensorflow.keras.callbacks import EarlyStopping


def split_tfdataset_into_3_parts(
    ds: tf.data.Dataset,
    train_size=0.8,
    val_size=0.1,
    shuffle=True,
    shuffle_size=10000,
):
    """Chia dataset thành tập train, val, test theo tỉ lệ nhất định

    Args:
        ds (tf.data.Dataset): _description_
        train_size (float, optional): _description_. Defaults to 0.8.
        val_size (float, optional): _description_. Defaults to 0.1.
        shuffle (bool, optional): _description_. Defaults to True.
        shuffle_size (int, optional): _description_. Defaults to 10000.

    Returns:
        train, val, test
    """
    ds_size = len(ds)

    if shuffle:
        ds = ds.shuffle(shuffle_size, seed=42)

    train_size = int(train_size * ds_size)
    val_size = int(val_size * ds_size)

    train_ds = ds.take(train_size)
    val_ds = ds.skip(train_size).take(val_size)
    test_ds = ds.skip(train_size).skip(val_size)

    return train_ds, val_ds, test_ds


def cache_prefetch_tfdataset(ds: tf.data.Dataset, shuffle_size=1000):
    return ds.cache().shuffle(shuffle_size).prefetch(buffer_size=tf.data.AUTOTUNE)


def split_tfdataset_into_2_parts(
    ds: tf.data.Dataset, test_size=0.2, shuffle=True, shuffle_size=10000
):
    """Chia dataset thành tập train, test theo tỉ lệ của tập test

    Returns:
        _type_: train_ds, test_ds
    """
    ds_size = len(ds)

    if shuffle:
        ds = ds.shuffle(shuffle_size, seed=42)

    test_size = int(test_size * ds_size)

    test_ds = ds.take(test_size)
    train_ds = ds.skip(test_size)

    return train_ds, test_ds


def get_classification_report(model, ds, class_names):
    """Get classification_report cho DL model

    Args:
        model (_type_): _description_
        ds (_type_): _description_
        class_names (_type_): _description_

    """
    y_true = []
    y_pred = []

    class_names = np.asarray(class_names)

    # Lặp qua các batch trong train_ds
    for images, labels in ds:
        # Dự đoán bằng mô hình
        predictions = model.predict(images, verbose=0)

        y_pred_batch = class_names[np.argmax(predictions, axis=-1)].tolist()
        y_true_batch = class_names[np.asarray(labels)].tolist()
        y_true += y_true_batch
        y_pred += y_pred_batch

    return metrics.classification_report(y_true, y_pred)


def plot_train_val_metric_per_epoch(history, metric):
    """Vẽ biểu đồ train-val metric theo từng epoch của Deep Learning model

    Args:
        history (_type_): _description_
        metric (_type_): Chỉ số cần vẽ, vd: loss, accuracy, mse, ...

    Returns:
        fig: _description_
    """
    num_epochs = len(history["loss"])
    epochs = range(1, num_epochs + 1)
    epochs = [str(i) for i in epochs]

    fig, ax = plt.subplots()
    ax.plot(epochs, history[metric], color="gray", label=metric)
    ax.plot(epochs, history["val_" + metric], color="blue", label="val_" + metric)
    ax.set_ylim(bottom=0)

    return fig


def split_classification_folder_into_two(
    src_dir: str, dest_dir: str, categories: list, dest_size=0.2
):
    """Chia classfication thư mục thành 2 thư mục
    - Thư mục **src** còn lại ban đầu
    - Thư mục **dest** mới được tạo ra có kích thước = **dest_size**

    Thư mục classfication có dạng sau:
    ```python
    train/
    ......pos/
    ......neg/
    ```

    Args:
        src_dir (str): Path thư mục nguồn
        dest_dir (str): Path thư mục đích
        categories (list): Các labels
        dest_size (float, optional): Kích cỡ của thư mục **dest** (thư mục được tạo mới) . Defaults to 0.2.
    """
    for category in categories:
        # Tạo thư mục dest
        os.makedirs(os.path.join(dest_dir, category))

        # Get tên các file và xáo trộn trước khi chia
        files = os.listdir(os.path.join(src_dir, category))
        random.Random(1337).shuffle(files)

        # Get tên các file sẽ chuyển sang dest
        num_dest_samples = int(dest_size * len(files))
        dest_files = files[:num_dest_samples]

        # Di chuyển các file
        for file_name in dest_files:
            shutil.move(
                os.path.join(src_dir, category, file_name),
                os.path.join(dest_dir, category, file_name),
            )


def split_classification_folder_into_three(
    src_dir, train_dir, val_dir, test_dir, categories, train_size, val_size
):
    # Tách tập train ra trước
    split_classification_folder_into_two(src_dir, train_dir, categories, train_size)

    # Tách tập val ra
    split_classification_folder_into_two(
        src_dir, val_dir, categories, val_size / (1 - train_size)
    )

    # Còn lại là tập test
    os.rename(src_dir, test_dir)


def copy_one_optimizer(optimizer):
    return optimizer.__class__.from_config(optimizer.get_config())


def copy_one_callback(callback):
    # Nếu là EarlyStopping
    if isinstance(callback, EarlyStopping):
        return EarlyStopping(
            monitor=callback.monitor,
            min_delta=callback.min_delta,
            patience=callback.patience,
            mode=callback.mode,
        )
    else:
        raise ValueError("Chỉ mới định nghĩa cho EarlyStopping")


def get_full_target_and_pred_for_softmax_model(model, ds):
    """Get full target và prediction cho các model mà kết thúc bằng layer Dense với activatoin = 'softmax'

    Args:
        model (_type_): model
        ds (_type_): dataset mà model sẽ dự đoán

    Returns:
        (y_true, y_pred): (Tập target, tập prediction)
    """
    y_true = []
    y_pred = []

    # Lặp qua các batch trong train_ds
    for feature, true_data in ds:
        # Dự đoán bằng mô hình
        predictions = model.predict(feature, verbose=0)

        y_pred_batch = np.argmax(
            predictions, axis=-1
        ).tolist()  # Convert về giống dạng của y_true_batch
        y_true_batch = true_data.numpy().tolist()  # Convert về list
        y_true += y_true_batch
        y_pred += y_pred_batch

    return y_true, y_pred


def get_full_target_and_pred_for_regression_model(model, ds):
    """Get full target và prediction cho regression model, tức là kết thúc bằng layer Dense(1)

    Args:
        model (_type_): _description_
        ds (_type_): _description_

    Returns:
        _type_: _description_
    """
    y_true = []
    y_pred = []

    # Lặp qua các batch trong train_ds
    for feature, true_data in ds:
        # Dự đoán bằng mô hình
        predictions = model.predict(feature, verbose=0)

        y_pred_batch = predictions.tolist()  # predictions có datatype = numpy array
        y_true_batch = true_data.numpy().tolist()  # Convert về list
        y_true += y_true_batch
        y_pred += y_pred_batch

    return y_true, y_pred


def get_full_target_and_pred_for_binary_model(model, ds):
    """Get full target và prediction cho binary classification model, tức là kết thúc bằng layer Dense(1, activation = 'sigmoid')

    Args:
        model (_type_): _description_
        ds (_type_): _description_

    Returns:
        _type_: _description_
    """
    y_true = []
    y_pred = []

    # Lặp qua các batch trong train_ds
    for feature, true_data in ds:
        # Dự đoán bằng mô hình
        predictions = model.predict(feature, verbose=0)

        y_pred_batch = (
            (predictions > 0.5).astype("int").tolist()
        )  # > 0.5 -> lớp 1, ngược lại là 0
        y_true_batch = true_data.numpy().tolist()  # Convert về list
        y_true += y_true_batch
        y_pred += y_pred_batch

    return y_true, y_pred


def convert_pairs_to_tf_dataset(pairs, batch_size):
    """Chuyển list các tuples (item1, item2) thành tf.data.Dataset với batch_size

    Args:
        pairs (_type_): các cặp
        batch_size (_type_): _description_
    """
    list_item1, list_item2 = zip(*pairs)
    list_item1 = list(list_item1)
    list_item2 = list(list_item2)

    # Tạo tf.data.Dataset và chia batch
    dataset = tf.data.Dataset.from_tensor_slices((list_item1, list_item2))
    dataset = dataset.batch(batch_size)

    return dataset


def save_text_vectorization(text_vectorization, file_path):
    vectorizer_model = tf.keras.Sequential([text_vectorization])
    vectorizer_model.save(file_path)


def load_text_vectorization(file_path):
    loaded_model = tf.keras.models.load_model(file_path)
    return loaded_model.layers[
        0
    ]  # Lúc save thì cho vào dummy model, nên lúc lấy ra thì get layer đầu tiên

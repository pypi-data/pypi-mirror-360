import pickle
import itertools
import re
import json
import pickle
import pandas as pd
from sklearn.model_selection import PredefinedSplit
import numpy as np
from sklearn.model_selection import (
    train_test_split,
    ParameterGrid,
    ParameterSampler,
)
from typing import Union
import pandas as pd
import numpy as np
import random
import os


SCORINGS_PREFER_MININUM = ["log_loss", "mse", "mae"]
SCORINGS_PREFER_MAXIMUM = ["accuracy"]


def get_index_of_outliers(data: Union[np.ndarray, list]):
    """Lấy **index** các giá trị outlier nằm ngoài khoảng Q1 - 1.5*IQR và Q3 + 1.5*IQR

    Args:
        data (Union[np.ndarray, list]): dữ liệu

    Returns:
        list:
    """
    data = np.asarray(data)
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    result = np.where((data < lower_bound) | (data > upper_bound))[0].tolist()

    return result


def get_index_of_outliers_on_series(data: pd.Series):
    """Lấy **index** các giá trị outlier nằm ngoài khoảng Q1 - 1.5*IQR và Q3 + 1.5*IQR

    Args:
        data (pd.Series): dữ liệu kiểu **pd.Series**

    Returns:
        list:
    """
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    result = data.index[(data < lower_bound) | (data > upper_bound)]

    return result


def get_lower_and_upper_bound_of_data(data):
    """Tìm lowerbound, upperbound của 1 tập dữ liệu

    Công thức:
    - lower_bound = Q1 - 1.5 * IQR
    - upper_bound = Q3 + 1.5 * IQR

    Returns:
        (lower_bound, upper_bound): _description_
    """
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    return lower_bound, upper_bound


def is_number_str(string_to_check: str):
    """Check if string_to_check is a number"""

    try:
        float(string_to_check)
        return True
    except ValueError:
        return False


def is_integer_str(s: str):
    """Check if str is an integer

    Args:
        s (str): _description_
    """

    regex = "^[+-]?\d+$"
    return bool(re.match(regex, s))


def is_natural_number_str(s: str):
    """Check if str is a natural_number

    Args:
        s (str): _description_
    """

    regex = "^\+?\d+$"
    return re.match(regex, s) is not None


def split_numpy_array_into_many_parts(
    data: np.ndarray, ratios: list, dimension=1, shuffle: bool = True
):
    """

    Args:
        data (np.ndarray): _description_
        ratios (list): Tỉ lệ các phần. Tổng phải bằng 1
        dimension (int, optional): Chiều của dữ liệu. nếu dữ liệu 2 chiều thì gán = 2. Defaults to 1.
        shuffle(bool, optional): có xáo trộn dữ liệu trước khi chia không

    Returns:
        list: list các mảng numpy

    vd:
    với dữ liệu 2 chiều:
    ```python
    split_ratios = [0.5, 0.2, 0.2, 0.1]  # Tỷ lệ mong muốn
    subsets = split_data(data, split_ratios, 2)
    ```
    """
    if sum(ratios) != 1:
        raise ValueError("Tổng của ratios phải bằng 1")

    if shuffle:
        data = np.random.permutation(data)

    len_data = len(data) if dimension == 1 else data.shape[0]
    split_indices = np.cumsum(ratios)[:-1] * len_data
    split_indices = split_indices.astype(int)
    return (
        np.split(data, split_indices)
        if dimension == 1
        else np.split(data, split_indices, axis=0)
    )


def split_dataframe_into_many_parts(
    data: pd.DataFrame, ratios: list, shuffle: bool = True
):
    """

    Args:
        data (pd.DataFrame): _description_
        ratios (list): Tỉ lệ các phần. Tổng phải bằng 1
        shuffle(bool, optional): có xáo trộn dữ liệu trước khi chia không. Defaults to True

    Returns:
        list: list các dataframe

    VD:
        ```python
    split_ratios = [0.5, 0.2, 0.2, 0.1]  # Tỷ lệ mong muốn
    subsets = split_data(data, split_ratios)
    """
    if sum(ratios) != 1:
        raise ValueError("Tổng của ratios phải bằng 1")

    if shuffle:
        data = data.sample(frac=1.0, random_state=42).reset_index(drop=True)

    split_indices = np.cumsum(ratios)[:-1] * len(data)
    split_indices = split_indices.astype(int)

    subsets = np.split(data, split_indices, axis=0)

    return [pd.DataFrame(item, columns=data.columns) for item in subsets]


def load_python_object(file_path):
    try:
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        raise e


def save_python_object(file_path, obj):
    """Save python object in a file

    Args:
        file_path (_type_): ends with .pkl
    """

    try:
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
    except Exception as e:
        raise e


def save_python_object_without_overwrite(file_path, obj):
    """Giống như hàm save_python_object nhưng khác là nếu file đó đã tồn tại thì không đè đối tượng mới"""
    if os.path.exists(file_path):
        return

    save_python_object(file_path, obj)


def get_features_target_spliter_for_CV_train_val(
    train_features, train_target, val_features, val_target
):
    """Get total features, target, spliter to do GridSearchCV or RandomisedSearchCV with type is **train-val**

    Args:
        train_features (dataframe): _description_
        train_target (dataframe): _description_
        val_features (dataframe): _description_
        val_target (dataframe): _description_
    Returns:
        features, target,       spliter


    """

    features = pd.concat([train_features, val_features], axis=0)
    target = pd.concat([train_target, val_target], axis=0)
    spliter = PredefinedSplit(
        test_fold=[-1] * len(train_features) + [0] * len(val_features)
    )

    return features, target, spliter


def get_features_target_spliter_for_CV_train_train(train_features, train_target):
    """Get total features, target, spliter to do GridSearchCV or RandomisedSearchCV with type is **train-train** <br>
    When you want to train on training set and assess on that training set


    Args:
        train_features (dataframe): _description_
        train_target (dataframe): _description_
        val_features (dataframe): _description_
        val_target (dataframe): _description_
    """

    features = pd.concat([train_features, train_features], axis=0)
    target = pd.concat([train_target, train_target], axis=0)
    spliter = PredefinedSplit(
        test_fold=[-1] * len(train_features) + [0] * len(train_features)
    )

    return features, target, spliter


def create_directories(path_to_directories: list):
    """create list of directories

    Args:
        path_to_directories (list): list of path of directories

    """

    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)


def create_directory(path_to_directory):
    """create a directory

    Args:
        path_to_directory (list): path to the directory

    """
    os.makedirs(path_to_directory, exist_ok=True)


def save_json(path: str, data: dict):
    """save json data

    Args:
        path (Path): path to json file
        data (dict): data to be saved in json file
    """

    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"json file saved at {path}")


def load_json(path: str):
    """load json files data

    Args:
        path (Path): path to json file

    Returns:
        ConfigBox: data as class attributes instead of dict
    """
    with open(path) as f:
        content = json.load(f)

    print(f"json file loaded succesfully from: {path}")
    return content


def describe_for_numeric_cat_cols(data):
    """Get descriptive statistics of numeric cat cols, including min, max, median

    Args:
        data (_type_): numeric cat cols
    Returns:
        Dataframe: min, max, median
    """

    min_of_cols = data.min().to_frame(name="min")
    max_of_cols = data.max().to_frame(name="max")
    median_of_cols = data.quantile([0.5]).T.rename(columns={0.5: "median"})

    result = pd.concat([min_of_cols, max_of_cols, median_of_cols], axis=1)

    return result


def get_different_types_cols_from_df(df: pd.DataFrame):
    """Tìm các cột kiểu numeric, numericCat, cat, binary, nominal, ordinal  target từ df

    Lưu ý: có tìm luôn cột **target**

    Returns:
        (numeric_cols, numericCat_cols, cat_cols, binary_cols, nominal_cols, ordinal_cols, target_col):
    """

    cols = pd.Series(df.columns)
    numeric_cols = cols[cols.str.endswith("num")].tolist()
    numericCat_cols = cols[cols.str.endswith("numcat")].tolist()
    binary_cols = cols[cols.str.endswith("bin")].tolist()
    nominal_cols = cols[cols.str.endswith("nom")].tolist()
    ordinal_cols = cols[cols.str.endswith("ord")].tolist()
    cat_cols = binary_cols + nominal_cols + ordinal_cols
    target_col = cols[cols.str.endswith("target")].tolist()[0]

    return (
        numeric_cols,
        numericCat_cols,
        cat_cols,
        binary_cols,
        nominal_cols,
        ordinal_cols,
        target_col,
    )


def get_different_types_feature_cols_from_df(df: pd.DataFrame):
    """Tìm các cột kiểu numeric, numericCat, cat, binary, nominal, ordinal từ df

    Lưu ý: Chỉ các cột **feature** không có cột **target**
    Returns:
        (numeric_cols, numericCat_cols, cat_cols, binary_cols, nominal_cols, ordinal_cols):
    """
    cols = pd.Series(df.columns)
    numeric_cols = cols[cols.str.endswith("num")].tolist()
    numericCat_cols = cols[cols.str.endswith("numcat")].tolist()
    binary_cols = cols[cols.str.endswith("bin")].tolist()
    nominal_cols = cols[cols.str.endswith("nom")].tolist()
    ordinal_cols = cols[cols.str.endswith("ord")].tolist()
    cat_cols = binary_cols + nominal_cols + ordinal_cols

    return (
        numeric_cols,
        numericCat_cols,
        cat_cols,
        binary_cols,
        nominal_cols,
        ordinal_cols,
    )


def get_target_col_from_df(df):
    """Get cột target từ df
    Returns:
        target_col: _description_
    """

    cols = pd.Series(df.columns)
    target_col = cols[cols.str.endswith("target")].tolist()[0]
    return target_col


def get_feature_cols_and_target_col_from_df(df):
    """Get các cột feature và cột target từ df

    Returns:
        (feature_cols, target_col): _description_
    """
    cols = pd.Series(df.columns)
    target_col = cols[cols.str.endswith("target")]
    feature_cols = cols.drop(target_col.index).tolist()
    target_col = target_col.tolist()[0]

    return feature_cols, target_col


def replace_in_category_series(series, replace_value_list: list):
    """Replace giá trị trong các cột kiểu category

    VD:
    ```
    a = pd.Series(['a', 'b', 'c', 'd', 'b', 'c', 'd'])

    # Thay a, b -> ab, c -> c1
    replace_value_list = [
        (['a', 'b'], 'ab'),
        (['c'], 'c1'),
    ]

    a = myfuncs.replace_in_category_series_33(a, replace_value_list)
    ```

    """
    series = series.astype("string")

    new_replace_value_list = [
        [item[0], [item[1]] * len(item[0])] for item in replace_value_list
    ]
    replace_value_dict_keys = itertools.chain(
        *[item[0] for item in new_replace_value_list]
    )
    replace_value_dict_values = itertools.chain(
        *[item[1] for item in new_replace_value_list]
    )
    replace_value_dict = dict(zip(replace_value_dict_keys, replace_value_dict_values))
    series = series.replace(replace_value_dict)
    series = series.astype("category")
    return series


def replace_in_series(series, replace_value_list: list):
    """Replace giá trị trong các cột kiểu bất kì ngoại trừ kiểu category <br>
    Nếu là kiểu category thì dùng hàm sau: replace_in_category_series_33

    VD:
    ```
    a = pd.Series(['a', 'b', 'c', 'd', 'b', 'c', 'd'])

    # Thay a, b -> ab, c -> c1
    replace_value_list = [
        (['a', 'b'], 'ab'),
        (['c'], 'c1'),
    ]

    a = myfuncs.replace_in_category_series_33(a, replace_value_list)
    ```

    """
    new_replace_value_list = [
        [item[0], [item[1]] * len(item[0])] for item in replace_value_list
    ]
    replace_value_dict_keys = itertools.chain(
        *[item[0] for item in new_replace_value_list]
    )
    replace_value_dict_values = itertools.chain(
        *[item[1] for item in new_replace_value_list]
    )
    replace_value_dict = dict(zip(replace_value_dict_keys, replace_value_dict_values))
    series = series.replace(replace_value_dict)
    return series


def replace_outliers_with_new_value(series, mode="mean"):
    """Thay thế các outliers trong 1 series thành giá trị mới"""
    new_value = None
    if mode == "mean":
        new_value = np.mean(series)
    elif mode == "median":
        new_value = np.percentile(series, 50)
    else:
        raise ValueError(
            f"Tham số mode = {mode} không hợp lệ cho hàm replace_outliers_with_new_value"
        )

    lb, ub = get_lower_and_upper_bound_of_data(series)
    series[series.index[(series < lb) | (series > ub)]] = new_value
    return series


def get_label_percent_in_categorical_column(series):
    """Phần trăm các label trong cột categorical"""
    return series.value_counts() / len(series) * 100


def get_outlier_percent_of_numeric_cols(df, numeric_cols):
    """Get phần trăm các outlier ở trong các cột numeric

    Returns:
        series:
    """
    list_outlier_percent = []
    for col in numeric_cols:
        lb, ub = get_lower_and_upper_bound_of_data(df[col])
        count_outlier = np.sum((df[col] < lb) | (df[col] > ub))
        outlier_percent = count_outlier / len(df[col]) * 100
        list_outlier_percent.append(outlier_percent)

    res = pd.Series(list_outlier_percent, index=numeric_cols)
    res = res.sort_values(ascending=False)
    return res


def get_cat_cols_from_df(df):
    """Get các cột categorical"""
    cols = pd.Series(df.columns)
    binary_cols = cols[cols.str.endswith("bin")].tolist()
    nominal_cols = cols[cols.str.endswith("nom")].tolist()
    ordinal_cols = cols[cols.str.endswith("ord")].tolist()
    cat_cols = binary_cols + nominal_cols + ordinal_cols

    return cat_cols


def get_numericcat_cols_from_df(df):
    """Get numericcat cột"""
    cols = pd.Series(df.columns)
    numericCat_cols = cols[cols.str.endswith("numcat")].tolist()

    return numericCat_cols


def get_min_max_of_numeric_cols(df, numeric_cols):
    """Get giá trị min, max của các cột numeric

    Returns:
        df: _description_
    """
    return df[numeric_cols].describe().loc[["min", "max"]].T


def get_numeric_cols_from_df(df):
    """Get numeric cột"""
    cols = pd.Series(df.columns)
    res = cols[cols.str.endswith("num")].tolist()

    return res


def log_series(series):
    """Tiến hành log 1 series

    Lưu ý: log(A) xác định khi A > 0 , nên ở đây thay thế các giá trị không dương bằng giá trị nhỏ nhất trong series mà > 0
    """
    if np.min(series) > 0:
        return np.log(series)

    # Tìm giá trị nhỏ nhất của series mà > 0
    min_series_g0 = np.min(series[series > 0])

    series[series < 0] = min_series_g0

    return np.log(series)


def log_many_columns(df, cols):
    """Log nhiều cột

    Args:
        df (_type_): _description_
        cols (_type_): tên các cột cần log
    """
    for col in cols:
        df[col] = log_series(df[col])


def split_df_into_two_in_stratified_fashion(df, train_size, col_for_stratified):
    df_train, df_val = train_test_split(
        df, test_size=(1 - train_size), stratify=df[col_for_stratified]
    )
    return df_train, df_val


def split_df_into_two(df, train_size):
    df_train, df_val = train_test_split(df, test_size=(1 - train_size))
    return df_train, df_val


def split_df_into_three_in_stratified_fashion(
    df, train_size, val_size, col_for_stratified
):
    """Tách df thành 3 tập con theo stratified fashion

    Args:
        df (_type_): _description_
        train_size (_type_): tỉ lệ tập train
        val_size (_type_): tỉ lệ tập val
        col_for_stratified (_type_): tên cột dùng cho stratified fashion

    Returns:
        (df_train, df_val, df_test): _description_
    """
    # Tách tập train ra trước
    df_train, df_rest = train_test_split(
        df, test_size=(1 - train_size), stratify=df[col_for_stratified]
    )

    # Phần còn lại chia thành 2 tập val , test
    test_size = 1 - train_size - val_size
    test_size_in_df_rest = test_size / (1 - train_size)
    df_val, df_test = train_test_split(
        df_rest, test_size=test_size_in_df_rest, stratify=df_rest[col_for_stratified]
    )

    return df_train, df_val, df_test


def split_df_into_three(df, train_size, val_size):
    """Chia df thành 3 tập train, val và test

    Args:
        df (_type_): _description_
        train_size (_type_): _description_
        val_size (_type_): _description_

    Returns:
        (df_train, df_val, df_test): _description_
    """
    # Tách tập train ra trước
    df_train, df_rest = train_test_split(df, test_size=(1 - train_size))

    # Phần còn lại chia thành 2 tập val , test
    test_size = 1 - train_size - val_size
    test_size_in_df_rest = test_size / (1 - train_size)
    df_val, df_test = train_test_split(df_rest, test_size=test_size_in_df_rest)

    return df_train, df_val, df_test


def split_df_into_three_without_shuffle(df, train_size, val_size):
    """Chia df thành 3 tập con và giữ trật tự của df, không xáo trộn df trước khi chia <br>
    Nếu mà dùng train_test_split thì df sẽ được xáo trộn trước rồi mới chia <br>
    Hàm này thì chia luôn chứ không hoán đổi gì hết

    Args:
        df (_type_): _description_
        train_size (_type_): tỉ lệ tập đầu tiên
        val_size (_type_): tỉ lệ tập thứ hai

    Returns:
        (df_train, df_val, df_test): _description_
    """
    num_train_sample = int(train_size * len(df))
    num_val_sample = int(val_size * len(df))

    df_train = df.iloc[:num_train_sample, :]
    df_val = df.iloc[num_train_sample : num_train_sample + num_val_sample, :]
    df_test = df.iloc[num_train_sample + num_val_sample :, :]

    return df_train, df_val, df_test


def split_a_list_into_three(list_data, train_size, val_size):
    """Chia 1 list thành 3 list con, kiểu như chia thành 3 tập train, val, test

    Args:
        list_data (_type_): _description_
        train_size (_type_): tỉ lệ tập train (tập đầu tiên)
        val_size (_type_): tỉ lệ tập val (tập thứ hai), phần còn lại là tập thứ ba

    Returns:
        (train_data, val_data, test_data): _description_
    """
    random.shuffle(list_data)
    num_train_samples = int(train_size * len(list_data))
    num_val_samples = int(val_size * len(list_data))

    train_data = list_data[:num_train_samples]
    val_data = list_data[num_train_samples : num_train_samples + num_val_samples]
    test_data = list_data[num_train_samples + num_val_samples :]

    return train_data, val_data, test_data


def read_content_from_file(logs_filepath):
    with open(logs_filepath, mode="r") as file:
        content = file.read()

    return content


def write_content_to_file(result, file_path):
    with open(file_path, mode="w") as file:
        file.write(result)


def randomize_dict(value_dict, num_sample):
    # Tính số tổ hợp trong value_dict
    total_combinations = 1
    for v in value_dict.values():
        total_combinations *= len(v)

    if num_sample > total_combinations:
        return list(ParameterGrid(value_dict))

    return list(ParameterSampler(value_dict, n_iter=num_sample, random_state=42))


def get_full_list_dict(value_dict):
    return list(ParameterGrid(value_dict))


def subtract_2list_set(A, a):
    """Trừ 2 danh sách, các phần tử trong danh sách là các set"""
    set_A = set(tuple(sorted(d.items())) for d in A)
    set_a = set(tuple(sorted(d.items())) for d in a)
    diff = set_A - set_a
    diff = [dict(t) for t in diff]
    return diff


def randomize_list(value_list, num_sample):
    """Random 1 list con gồm num_sample phần tử từ value_list"""
    if num_sample > len(value_list):
        return value_list

    return random.sample(value_list, num_sample)

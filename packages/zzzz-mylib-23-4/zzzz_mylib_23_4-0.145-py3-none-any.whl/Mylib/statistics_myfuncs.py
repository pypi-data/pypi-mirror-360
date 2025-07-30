import pickle
import itertools
import re
import json
import pickle
import pandas as pd
from sklearn.model_selection import PredefinedSplit
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.model_selection import (
    GridSearchCV,
    train_test_split,
    ParameterGrid,
    ParameterSampler,
)
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt
from typing import Union
from sklearn import metrics
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.stats import chi2_contingency
from scipy import stats
from sklearn.feature_selection import (
    SelectKBest,
    mutual_info_regression,
    mutual_info_classif,
)
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
import random
import os


def get_pvalue_for_test_relation_between_cat_col_and_numeric_col(
    df, cat_col, numeric_col
):
    """Test mức độ ảnh hưởng của 1 biến categorical đến biến numeric target

    Args:
        df (_type_): _description_
        cat_col (_type_): _description_
        target_col (_type_): Phải là biến numeric !!!!!

    Returns:
        p_value: _description_
    """
    data = df.groupby(cat_col)[numeric_col].apply(list)
    p_value = stats.kruskal(*list(data.values)).pvalue
    return p_value


def get_pvalue_for_test_relation_between_numeric_features_and_cat_target(
    df, numeric_cols, target_col
):
    """Kiểm định mức độ ảnh hưởng của các biến numeric đến biến target phân loại

    Args:
        df (_type_): _description_
        numeric_cols (_type_): _description_
        target_col (_type_): Phải là biến phân loại

    Returns:
        series: _description_
    """
    list_p_value = [
        get_pvalue_for_test_relation_between_cat_col_and_numeric_col(
            df, target_col, col
        )
        for col in numeric_cols
    ]
    res = pd.Series(list_p_value, index=numeric_cols)
    res = res.sort_values(ascending=True)
    return res


def get_skew_on_numeric_cols(df, numeric_cols):
    """Get hệ số skew của các cột numeric

    Returns:
        series: _description_
    """
    list_skew = [np.abs(stats.skew(df[col])) for col in numeric_cols]
    res = pd.Series(list_skew, index=numeric_cols)
    res = res.sort_values(ascending=False)
    return res


def get_pvalue_chi_square_test_for_categorical_cols(df, cat_cols):
    """Thực hiện kiểm định cho các cột categoricals trong df

    Args:
        df (_type_): _description_
        cat_cols (_type_): tên các cột categorical

    Returns:
        df: Gồm có 3 cột, item0, item1, p_value
    """
    combinations_2 = list(itertools.combinations(cat_cols, 2))
    list_p_value = [
        get_pvalue_for_chi_square_test_for_2_variables(df, item[0], item[1])
        for item in combinations_2
    ]
    res = pd.Series(list_p_value, index=combinations_2)
    res = res.sort_values(ascending=True)

    return res


def get_pvalue_for_chi_square_test_between_categorical_cols_and_categorical_target_col(
    df, cat_cols, target_col
):
    list_p_value = [
        get_pvalue_for_chi_square_test_for_2_variables(df, col, target_col)
        for col in cat_cols
    ]

    res = pd.Series(list_p_value, index=cat_cols)
    res = res.sort_values(ascending=True)
    return res


def get_correlation_between_numeric_cols(df, numeric_cols):
    """Get hệ số tương quan của các cột numeric

    Returns:
        df: item0, item1, correlation
    """
    combinations_2 = list(itertools.combinations(numeric_cols, 2))
    res = [np.abs(df[item[0]].corr(df[item[1]])) for item in combinations_2]

    res = pd.Series(res, index=combinations_2)
    res = res.sort_values(ascending=False)

    return res


def get_correlation_between_numeric_features_and_numeric_target(
    df, numeric_cols, target_col
):
    correlations = [np.abs(df[col].corr(df[target_col])) for col in numeric_cols]
    res = pd.Series(correlations, index=numeric_cols)
    res = res.sort_values(ascending=False)


def get_pvalue_for_chi_square_test_for_2_variables(df, cat_col1, cat_col2):
    """Thực hiện kiểm định chi square cho 2 biến categorical trong df

    Args:
        df (_type_):
        cat_col1 (_type_): cột thứ 1
        cat_col2 (_type_): cột thứ 2

    Returns:
        p_value: Giá trị p_value của kiểm định
    """
    table = df.groupby([cat_col1, cat_col2]).size().unstack()
    return chi2_contingency(table.values)[1]

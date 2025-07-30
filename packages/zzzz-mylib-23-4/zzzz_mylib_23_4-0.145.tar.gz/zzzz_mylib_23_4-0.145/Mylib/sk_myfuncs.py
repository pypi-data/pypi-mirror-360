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


def find_feature_importances(train_data, model):
    """Find the feature importances of some models like: RF, GD, SGD, LGBM

    Returns:
        pd.DataFrame:
    """

    score = pd.DataFrame(
        data={
            "feature": train_data.columns.tolist(),
            "score": model.feature_importances_,
        }
    )
    score = score.sort_values(by="score", ascending=False)
    return score


def find_coef_from_classifier_model(train_data, model):
    """Find the feature importances of some models like: LR1, LRe

    Returns:
        pd.DataFrame:
    """

    score = pd.DataFrame(
        data={
            "feature": train_data.columns.tolist(),
            "score": np.abs(model.coef_[0]),
        }
    )
    score = score.sort_values(by="score", ascending=False)
    return score


def find_coef_from_regressor_model(train_data, model):
    """Find the feature importances of some models like: ElasticNet, Lasso

    Returns:
        pd.DataFrame:
    """

    score = pd.DataFrame(
        data={
            "feature": train_data.columns.tolist(),
            "score": np.abs(model.coef_),
        }
    )
    score = score.sort_values(by="score", ascending=False)
    return score


def find_best_n_components_of_PCA(
    train_features,
    train_target,
    val_features,
    val_target,
    placeholdout_model,
    list_n_components,
    scoring="accuracy",
):
    """Find best n_components of PCA

    Args:
        placeholdout_model (_type_): model like LR, XGB, ... without hyperparameters except random_state
        list_n_components (_type_): list of n_components used
        scoring (str, optional): scoring. Defaults to "accuracy".

    Returns:
        _type_: best n_components
    """
    features, target, splitter = get_features_target_spliter_for_CV_train_val(
        train_features, train_target, val_features, val_target
    )
    param_grid = {"1__n_components": list_n_components}
    pp = Pipeline(
        steps=[
            ("1", PCA(random_state=42)),
            ("2", placeholdout_model),
        ]
    )
    gs = GridSearchCV(pp, param_grid=param_grid, cv=splitter, scoring=scoring)
    gs.fit(features, target)
    return gs.best_params_


def find_feature_score_by_permutation_importance(
    train_features, train_target, fitted_model
):
    """Find the feature score by doing permutation_importance

    Args:
        fitted_model (_type_): fitted model, not base model

    Returns:
        DataFrame: _description_
    """
    result = permutation_importance(
        fitted_model, train_features, train_target, n_repeats=10, random_state=42
    )
    result_df = pd.DataFrame(
        data={
            "feature": train_features.columns.tolist(),
            "score": result.importances_mean * 100,
        }
    )
    result_df = result_df.sort_values(by="score", ascending=False)
    return result_df


def evaluate_model_on_one_scoring(model, feature, target, scoring):
    SCORINGS = ["accuracy", "mse", "mae", "roc_auc"]

    if scoring == "accuracy":
        prediction = model.predict(feature)
        return metrics.accuracy_score(target, prediction)

    if scoring == "mse":
        prediction = model.predict(feature)
        return np.sqrt(metrics.mean_squared_error(target, prediction))

    if scoring == "mae":
        prediction = model.predict(feature)
        return metrics.mean_absolute_error(target, prediction)

    if scoring == "roc_auc":
        prediction_proba = model.predict_proba(feature)[:, 1]
        return metrics.roc_auc_score(target, prediction_proba)

    raise ValueError(f"===== Chỉ mới định nghĩa cho {SCORINGS} ==============")


def get_classification_report(model, feature, target, class_names: list):
    """Tạo classfication report cho classifier"""
    class_names = np.asarray(class_names)

    target = [int(item) for item in target]
    target = class_names[target]

    prediction = model.predict(feature)
    prediction = [int(item) for item in prediction]
    prediction = class_names[prediction]

    return metrics.classification_report(target, prediction)


def get_confusion_matrix_heatmap(model, feature, target, class_names: list):
    """Vẽ confustion matrix heatmap

    Returns:
        fig: _description_
    """
    class_names = np.asarray(class_names)

    target = [int(item) for item in target]
    target = class_names[target]

    prediction = model.predict(feature)
    prediction = [int(item) for item in prediction]
    prediction = class_names[prediction]

    labels = np.unique(target)
    cm = metrics.confusion_matrix(target, prediction, labels=labels)
    np.fill_diagonal(cm, 0)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm,
        cbar=True,
        annot=True,
        cmap="YlOrRd",
        ax=ax,
        xticklabels=labels,
        yticklabels=labels,
    )

    return fig


def get_heatmap_for_confusion_matrix(confusion_matrix, labels):
    """Get heatmap cho confusion matrix

    Returns:
        fig: đối tượng chart
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        confusion_matrix,
        cbar=True,
        annot=True,
        cmap="YlOrRd",
        ax=ax,
        xticklabels=labels,
        yticklabels=labels,
    )

    return fig


def do_kbest_feature_selection_for_classification(transformed_features, target):
    """Thực hiện select kbest choa bài toán classification

    Args:
        transformed_features (_type_): **Phải được transformed trước**
        target (_type_): _description_

    Returns:
        series: _description_
    """
    # Khởi tạo selector
    selector = SelectKBest(score_func=mutual_info_classif, k="all")  # Classification

    # Fit cái đã
    selector.fit(transformed_features, target)  # features phải được transformed trước

    # Ghi lại kết quả điểm số
    res = pd.Series(selector.scores_, index=transformed_features.columns)
    res = res.sort_values(ascending=False)
    return res


def do_kbest_feature_selection_for_regression(transformed_features, target):
    """Thực hiện select kbest choa bài toán regression

    Args:
        transformed_features (_type_): **Phải được transformed trước**
        target (_type_): _description_

    Returns:
        series: _description_
    """
    # Khởi tạo selector
    selector = SelectKBest(score_func=mutual_info_regression, k="all")  # Regression

    # Fit cái đã
    selector.fit(transformed_features, target)  # features phải được transformed trước

    # Ghi lại kết quả điểm số
    res = pd.Series(selector.scores_, index=transformed_features.columns)
    res = res.sort_values(ascending=False)
    return res


def find_silhouette_score_for_each_param_for_DBSCAN(features, list_param):
    """Get chỉ số silhouette_score cho từng cặp tham số của DBSCAN

    Args:
        features (_type_): dữ liệu các đặc trưng
        list_param (_type_): list các tuple dạng (eps, min_samples)

    Returns:
        series: _description_
    """
    scores = []

    for param in list_param:
        eps, min_samples = param
        db = DBSCAN(eps=eps, min_samples=min_samples)
        labels = db.fit_predict(features)

        # Tính silhouette score chỉ khi có ít nhất 2 cụm
        score = silhouette_score(features, labels) if len(set(labels)) > 1 else None
        scores.append(score)

    res = pd.Series(scores, index=list_param)
    res = res.sort_values(ascending=False)
    return res


def get_noise_sample_by_DBSCAN(features, dbscan_model):
    """Tìm các điểm noise bằng thuật toán DBSCAN

    Args:
        features (_type_): _description_
        dbscan_model (_type_): _description_

    Returns:
        df: _description_
    """
    labels = dbscan_model.fit_predict(features)
    res = features[labels == -1, :]
    return res


def convert_list_estimator_into_pipeline(list_estimator):
    # Nểu là None hoặc rống thì return passthrough
    if list_estimator is None or len(list_estimator) == 0:
        return Pipeline(steps=[("passthrough", "passthrough")])

    return Pipeline(
        steps=[
            (str(index), transformer)
            for index, transformer in enumerate(list_estimator)
        ]
    )


def plot_explained_variance_ratio_of_PCA(data):
    pca = PCA()
    pca.fit(data)
    cumsum = np.cumsum(pca.explained_variance_ratio_)

    fig = px.line(
        x=list(range(1, len(cumsum) + 1)),
        y=cumsum,
        markers=True,
    )
    return fig


def plot_explained_variance_ratio_of_PCA_plt(data):
    pca = PCA()
    pca.fit(data)
    cumsum = np.cumsum(pca.explained_variance_ratio_)
    list_n_components = list(range(1, len(cumsum) + 1))

    plt.plot(list_n_components, cumsum, color="blue")
    plt.grid(True)
    plt.show()

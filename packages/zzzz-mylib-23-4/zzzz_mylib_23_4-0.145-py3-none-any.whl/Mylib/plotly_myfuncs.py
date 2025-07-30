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


def plot_hist_box_violin_plots_for_numeric_cols(df, numeric_cols):
    """Vẽ hist, boxplot, violin cho các cột số trong df

    Returns:
        fig: _description_
    """
    subplot_titles = sum(([item, "", ""] for item in numeric_cols), [])

    fig = make_subplots(rows=len(numeric_cols), cols=3, subplot_titles=subplot_titles)

    for row, col in enumerate(numeric_cols, 1):
        data = df[col]

        # Vẽ Histogram
        fig_hist = px.histogram(
            x=data,
            nbins=100,
        )

        # Thêm đường viền cho các cột histogram
        fig_hist.update_traces(marker=dict(line=dict(width=1, color="black")))

        # Vẽ box plot
        fig_box = px.box(
            y=data,
        )

        # Vẽ violin plot
        fig_violin = px.violin(
            y=data,
            box=True,
        )

        fig.add_trace(fig_hist.data[0], row=row, col=1)
        fig.add_trace(fig_box.data[0], row=row, col=2)
        fig.add_trace(fig_violin.data[0], row=row, col=3)

    fig.update_layout(
        width=300 * 3,  # Độ rộng biểu đồ (px)
        height=len(numeric_cols) * 400,  # Độ cao biểu đồ (px)
    )

    return fig


def plot_label_percent_for_categorical_cols(df, cat_cols):
    """Vẽ phần trăm các label trong các cột categorical

    Returns:
        fig: _description_
    """
    if cat_cols == []:
        return

    if len(cat_cols) == 1:
        cat_cols = [cat_cols[0], cat_cols[0]]

    fig = make_subplots(rows=len(cat_cols), cols=1, subplot_titles=cat_cols)

    for row, col in enumerate(cat_cols, 1):
        data = df[col]

        # Vẽ phân phối các label
        label_percent = data.value_counts() / len(data) * 100
        fig_bar = px.bar(x=label_percent.values, y=label_percent.index, orientation="h")

        fig.add_trace(fig_bar.data[0], row=row, col=1)

    fig.update_layout(
        width=300,  # Độ rộng biểu đồ (px)
        height=len(cat_cols) * 400,  # Độ cao biểu đồ (px)
    )

    return fig


def plot_label_percent_for_one_categorical_col(data):
    # Vẽ phân phối các label
    label_percent = data.value_counts() / len(data) * 100
    fig_bar = px.bar(x=label_percent.values, y=label_percent.index, orientation="h")

    return fig_bar

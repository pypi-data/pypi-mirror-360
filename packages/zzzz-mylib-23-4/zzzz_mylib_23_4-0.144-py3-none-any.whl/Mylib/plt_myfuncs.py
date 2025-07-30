import matplotlib.pyplot as plt
import seaborn as sns


def plot_hist_box_violin_plots_for_numeric_cols(df, numeric_cols):
    """Vẽ hist, boxplot, violin cho các cột số trong df

    Returns:
        fig: _description_
    """
    # Nếu không có cột nào thì return
    if numeric_cols == []:
        return

    # Xử lí trường hợp chỉ có 1 cột numeric
    if len(numeric_cols) == 1:
        numeric_cols = [numeric_cols[0], numeric_cols[0]]

    # Tạo một figure và các axes
    fig, axes = plt.subplots(
        nrows=len(numeric_cols), ncols=3, figsize=(15, len(numeric_cols) * 5)
    )

    for row, col in enumerate(numeric_cols):
        data = df[col]

        # Vẽ Histogram
        axes[row, 0].hist(data, bins=100, edgecolor="black")
        axes[row, 0].set_title(f"Histogram: {col}")
        axes[row, 0].set_xlabel(col)
        axes[row, 0].set_ylabel("Frequency")

        # Vẽ Box plot
        sns.boxplot(y=data, ax=axes[row, 1])
        axes[row, 1].set_title(f"Box plot: {col}")
        axes[row, 1].set_xlabel(col)

        # Vẽ Violin plot
        sns.violinplot(y=data, ax=axes[row, 2])
        axes[row, 2].set_title(f"Violin plot: {col}")
        axes[row, 2].set_xlabel(col)

    # Điều chỉnh không gian giữa các biểu đồ
    plt.tight_layout()
    return fig


def plot_label_percent_for_categorical_cols(df, cat_cols):
    """Vẽ phần trăm các label trong các cột categorical

    Returns:
        fig: _description_
    """
    # Tạo figure và axes
    fig, axes = plt.subplots(
        nrows=len(cat_cols), ncols=1, figsize=(8, len(cat_cols) * 3)
    )

    for row, col in enumerate(cat_cols):
        data = df[col]

        # Tính tỷ lệ phần trăm của các label
        label_percent = data.value_counts() / len(data) * 100

        # Vẽ bar plot (horizontally)
        axes[row].barh(
            label_percent.index,
            label_percent.values,
            color="skyblue",
            edgecolor="black",
        )
        axes[row].set_title(f"Label Percent for: {col}")
        axes[row].set_xlabel("Percentage (%)")
        axes[row].set_ylabel("Labels")

    # Điều chỉnh không gian giữa các biểu đồ
    plt.tight_layout()

    return fig


def plot_label_percent_for_one_categorical_col(data):
    fig, ax = plt.subplots()

    # Tính tỷ lệ phần trăm của các label
    label_percent = data.value_counts() / len(data) * 100

    # Vẽ bar plot (horizontally)
    ax.barh(
        label_percent.index,
        label_percent.values,
        color="skyblue",
        edgecolor="black",
    )
    ax.set_title(f"Label Percent")
    ax.set_xlabel("Percentage (%)")
    ax.set_ylabel("Labels")

    return fig

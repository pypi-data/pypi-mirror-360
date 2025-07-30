# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20250301

from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import torch


def diff_distribution(
    diff: Union[np.ndarray, torch.Tensor],
    figsize=(12, 5),
    dpi=200,
    with_title=True,
) -> plt.Figure:
    """
    Plot the distribution of errors in a histogram and box plot.

    Args:
        diff (Union[np.ndarray, torch.Tensor]): diff array containing the errors, such as diff = y_true - y_pred.
        figsize (tuple, optional): Figure size. Defaults to (12, 5).
        dpi (int, optional): Dots per inch for the figure. Defaults to 200.

    Returns:
        plt.Figure: Figure object containing the plots.
    """

    diff = np.array(diff).flatten()

    # calculate font size based on figure size
    title_fontsize = int(figsize[0] * 1.2)
    label_fontsize = int(figsize[0] * 1.0)

    fig, axes = plt.subplots(1, 2, figsize=figsize, dpi=dpi)
    axes[0].hist(diff, bins=30, color="skyblue", edgecolor="black", alpha=0.7)
    if with_title:
        axes[0].set_title(
            "Error Distribution (Histogram)", fontsize=title_fontsize
        )
    axes[0].set_xlabel("Error", fontsize=label_fontsize)
    axes[0].set_ylabel("Frequency", fontsize=label_fontsize)

    axes[1].boxplot(
        diff,
        vert=True,
        patch_artist=True,
        boxprops=dict(facecolor="lightcoral"),
    )
    if with_title:
        axes[1].set_title("Error Box Plot", fontsize=title_fontsize)
    axes[1].set_ylabel("Error", fontsize=label_fontsize)

    plt.tight_layout()
    return fig

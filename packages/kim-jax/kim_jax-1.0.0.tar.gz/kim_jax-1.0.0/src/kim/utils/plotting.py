"""Plotting functions."""

import pandas as pd
import seaborn as sns
import matplotlib as mpl

# TODO: Add plotting functions for
#       -  (conditional) sensitivity heat maps
#       -  loss over epochs
#       -  ????

def plot_sensitivity(sensitivity_mask, ax=None, xlabels=None, ylabels=None):

    if xlabels is not None and ylabels is not None:
       sensitivity_mask = pd.DataFrame(sensitivity_mask, index=xlabels, columns=ylabels)

    ax = sns.heatmap( sensitivity_mask, ax=ax, cmap='Blues')
    ax.set(title='Sensitivity heatmap')


def plot_sensitivity_mask(sensitivity_mask, ax=None, xlabels=None, ylabels=None):
    # define the colors
    cmap = mpl.colors.ListedColormap(['lightgrey', 'tab:blue'])

    # create a normalize object the describes the limits of
    # each color
    bounds = [-.5, 0.5, 1.5]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    if xlabels is not None and ylabels is not None:
       sensitivity_mask = pd.DataFrame(sensitivity_mask, index=xlabels, columns=ylabels)

    ax = sns.heatmap(
        sensitivity_mask, ax=ax, cmap=cmap, norm=norm, 
        cbar_kws={"ticks": [0, 1]}
      )
    ax.collections[0].colorbar.set_ticklabels(["not sensitive", "sensitive"], rotation=90)
    ax.set(title='Sensitivity mask')


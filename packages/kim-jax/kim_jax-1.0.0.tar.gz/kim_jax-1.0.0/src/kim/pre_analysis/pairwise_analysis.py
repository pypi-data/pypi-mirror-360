"""Pairwise analysis using either mutual information or correlation coefficient"""

# Author: Peishi Jiang <shixijps@gmail.com>

import numpy as np

from .sst import shuffle_test
from .metric_calculator import MetricBase
from tqdm import tqdm

from jaxtyping import Array


def pairwise_analysis(
    xdata: Array, ydata: Array, metric_calculator: MetricBase, sst: bool=False, 
    ntest: int=100, alpha: float=0.05, n_jobs: int=-1, seed_shuffle: int=1234, verbose: int=0
):
    """Perform the pairwise analysis.

    Args:
        xdata (array-like): the predictors with shape (Ns, Nx)
        ydata (array-like): the predictands with shape (Ns, Ny)
        metric_calculator (class): the metric calculator
        sst (bool): whether to perform statistical significance test. Defaults to False.
        ntest (int): number of shuffled samples in sst. Defaults to 100.
        alpha (float): the significance level. Defaults to 0.05.
        n_jobs (int): the number of processers/threads used by joblib. Defaults to -1.
        seed_shuffle (int): the random seed number for doing shuffle test. Defaults to 1234.
        verbose (int): the verbosity level (0: normal, 1: debug). Defaults to 0.

    Returns:
        (array, array): the sensitivity result
    """
    # Data dimensions
    assert xdata.shape[0] == ydata.shape[0], \
        "xdata and ydata must be the same number of samples"
    # Ns = xdata.shape[0]
    Nx = xdata.shape[1]
    Ny = ydata.shape[1]

    # Initialize the return sensitivity values and masks
    sensitivity = np.zeros([Nx, Ny])
    sensitivity_mask = np.ones([Nx, Ny], dtype='bool')

    if verbose == 1:
        print("Performing pairwise analysis to remove insensitive inputs ...")

    for i in tqdm(range(Nx)):
        x = xdata[:,i]
        for j in range(Ny):
            y = ydata[:,j]
            if not sst:
                sensitivity[i, j] = metric_calculator(x, y)
            else:
                metric, significance = shuffle_test(
                    x, y, metric_calculator, None, ntest, alpha, 
                    n_jobs=n_jobs, random_seed=seed_shuffle
                )
                sensitivity[i, j] = metric
                sensitivity_mask[i, j] = significance
    
    return sensitivity, sensitivity_mask

        
"""The PC algorithm suited to the X --> Y mapping problem."""

# Author: Peishi Jiang <shixijps@gmail.com>

import numpy as np

from .sst import shuffle_test
from .pairwise_analysis import pairwise_analysis
from .metric_calculator import MetricBase

from jaxtyping import Array


def pc(xdata: Array, ydata: Array, metric_calculator: MetricBase, cond_metric_calculator: MetricBase, 
       ntest: int=100, alpha: float=0.05, Ncond_max: int=3, n_jobs: int=-1, seed_shuffle: int=1234,
       verbose: int=0
    ):
    """The modified PC algorithm adapted to the X --> Y mapping problem.

    Args:
        xdata (array-like): the predictors with shape (Ns, Nx)
        ydata (array-like): the predictands with shape (Ns, Ny)
        metric_calculator (class): the metric calculator for unconditional relation
        cond_metric_calculator (class): the metric calculator for conditional relation
        ntest (int): number of shuffled samples in sst. Defaults to 100.
        alpha (float): the significance level. Defaults to 0.05.
        Ncond_max (int): the maximum number of conditions used by cond_metric_calculator. Defaults to 3.
        n_jobs (int): the number of processers/threads used by joblib. Defaults to -1.
        seed_shuffle (int): the random seed number for doing shuffle test. Defaults to 1234.
        verbose (int): the verbosity level (0: normal, 1: debug). Defaults to 0.

    Returns:
        (array, array, array): the sensitivity result
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
    cond_sensitivity_mask = np.ones([Nx, Ny], dtype='bool')

    # Perform the pairwise analysis
    # shape: (Nx, Ny)
    sensitivity, sensitivity_mask = pairwise_analysis(
        xdata, ydata, metric_calculator, True, ntest, alpha, verbose=verbose
    )
    cond_sensitivity_mask = sensitivity_mask.copy()

    # Order the sensitivity results
    # shape: (Nx, Ny)
    sensitivity_order = np.argsort(sensitivity, axis=0)[::-1,:]

    if verbose == 1:
        print("Performing conditional independence testing to remove redundant inputs ...")

    # Perform the conditional pairwise analysis
    for yj in range(Ny):  # For each target predictand
        y = ydata[:,yj]

        # Sort the condition based on sensitivity_order
        # from the strongest to least sensitivity
        cond_sens_mask_yj = cond_sensitivity_mask[sensitivity_order[:,yj],yj]
        # print(sensitivity_order[:,yj])
        # print(sensitivity[:,yj])
        # print(cond_sens_mask_yj)

        # Get the significant x based on sensitivity_mask
        # cond_all = np.where(cond_sens_mask_yj)[0]
        cond_all = sensitivity_order[cond_sens_mask_yj, yj]
        if len(cond_all) <= 1:
            continue

        # # Additional insignificant predictor
        # insig_x = []

        # Get the maximum number of condition sets for yj
        Ncond_max_j = min(Ncond_max, len(cond_all))

        # Loop over the number of conditions
        for k in range(1, Ncond_max_j+1):

            # We start with the one with the least sensitivity
            cond_all_reversed = cond_all[::-1]
            for i,xi in enumerate(cond_all_reversed):
                x = xdata[:, xi]

                # Get the condition data
                cond_all_but_xi = cond_all[cond_all != xi]
                cond = cond_all_but_xi[:k]
                xc = xdata[:, cond]

                # Perform the conditional pairwise analysis
                metric, significance = shuffle_test(
                    x, y, cond_metric_calculator, cdata=xc, ntest=ntest, alpha=alpha,
                    n_jobs=n_jobs, random_seed=seed_shuffle
                )
                # print(xc.shape, cond_all_but_xi.shape, cond_all.shape, yj, xi, cond, k, significance)

                # Check the shuffle test result
                if not significance:
                    cond_sensitivity_mask[xi, yj] = False
                    # insig_x.append(xi)
                    # insig_x.append(i)
                    # Remove insig_x from cond_all
                    cond_all = cond_all[cond_all != xi]

                # If there is no or only one predictor remains, continue
                if len(cond_all) <= 1:
                    break
            
            # # Remove insig_x from cond_all
            # cond_all = np.delete(cond_all, insig_x)

            # If there is no or only one predictor remains, continue
            if len(cond_all) <= 1:
                break
        
    return sensitivity, sensitivity_mask, cond_sensitivity_mask
"""Statistical significance test or shuffle test"""

# Author: Peishi Jiang <shixijps@gmail.com>

import numpy as np
from joblib import Parallel, delayed

from .metric_calculator import MetricBase

from typing import Optional
from jaxtyping import Array


def shuffle_test(
    x: Array, y: Array, metric_calculator: MetricBase, cdata: Optional[Array]=None, 
    ntest: int=100, alpha: float=0.05, n_jobs: int=-1, random_seed: int=1234):
    """Shuffle test.

    Args:
        x (array): the x data with dimension (Ns,)
        y (array): the x data with dimension (Ns,)
        cdata (array): the x data with dimension (Ns,Nc)
        metric_calculator (class): the metric calculator
        ntest (int): number of shuffled samples in sst. Defaults to 100.
        alpha (float): the significance level. Defaults to 0.05.
        n_jobs (int): the number of processers/threads used by joblib. Defaults to -1.
        random_seed (int): the random seed number. Defaults to 1234.

    Returns:
        (float, bool): metric_value, significance_or_not
    """
    if random_seed is None:
        np.random.seed()
    else:
        np.random.seed(random_seed)
    
    # Calculate the reference metric
    if cdata is None:
        metrics = metric_calculator(x, y)
    else:
        metrics = metric_calculator(x, y, cdata)

    # Calculate the suffled metrics
    # metrics_shuffled_all = np.zeros(ntest)
    # for i in range(ntest):
    #     # Get shuffled data
    #     x_shuffled = np.random.permutation(x)

    #     # Calculate the corresponding mi
    #     if cdata is None:
    #         metrics_shuffled = metric_calculator(x_shuffled, y)
    #     else:
    #         metrics_shuffled = metric_calculator(x_shuffled, y, cdata)

    #     metrics_shuffled_all[i] = metrics_shuffled
    # Get shuffled data
    x_shuffled_all = [np.random.permutation(x) for i in range(ntest)]

    # def shuffle(x, y, cdata, metric_calculator):
        # # Get shuffled data
        # x_shuffled = np.random.permutation(x)

    def shuffle(x_shuffled, y, cdata, metric_calculator):
        # Calculate the corresponding mi
        if cdata is None:
            metrics_shuffled = metric_calculator(x_shuffled, y)
        else:
            metrics_shuffled = metric_calculator(x_shuffled, y, cdata) 
        return metrics_shuffled

    # n_jobs = ntest
    metrics_shuffled_all = Parallel(n_jobs=n_jobs, backend='loky')(
        delayed(shuffle)(x_shuffled_all[i], y, cdata, metric_calculator) for i in range(ntest)
    )
    metrics_shuffled_all = np.array(metrics_shuffled_all)

    # Calculate 95% and 5% percentiles
    upper = np.percentile(metrics_shuffled_all, int(100*(1-alpha)))
    # lower = np.percentile(metrics_shuffled_all, int(100*alpha))

    # Return
    if metrics > upper:
        return metrics, True
    else:
        return 0.0, False


# def cond_shuffle_test(x, y, xc, cond_metric_calculator, ntest=100, alpha=0.05, random_seed=1234):
#     pass
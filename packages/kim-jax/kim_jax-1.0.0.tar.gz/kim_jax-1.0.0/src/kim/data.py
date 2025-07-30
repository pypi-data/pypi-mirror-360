"""The general data class."""

# Author: Peishi Jiang <shixijps@gmail.com>

import numpy as np

import json
import pickle
from pathlib import Path, PosixPath

from .pre_analysis import analyze_interdependency
from .utils import get_scaler

from jaxtyping import Array


class Data(object):
    """Data object.

    Arguments:
    ----------
    xdata (array-like): the predictors with shape (Ns, Nx)
    ydata (array-like): the predictands with shape (Ns, Ny)

    Attributes
    ----------
    self.xdata (array-like): the copy of xdata
    self.ydata (array-like): the copy of ydata
    self.Ns (int): the number of samples
    self.Nx (int): the number of predictors
    self.Ny (int): the number of predictands
    self.xscaler_type (str): the type of xdata scaler, either 'minmax', 'normalize', 'standard', or 'log'
    self.yscaler_type (str): the type of ydata scaler, either 'minmax', 'normalize', 'standard', or 'log'
    self.xscaler (str): the xdata scaler
    self.yscaler (str): the ydata scaler
    self.sensitivity_config (dict): the sensitivity analysis configuration
    self.sensitivity_done (bool): whether the sensitivity analysis is performed
    self.sensitivity (array-like): the calculated sensitivity with shape (Nx, Ny)
    self.sensitivity_mask (array-like): the calculated sensitivity mask with shape (Nx, Ny)
    self.cond_sensitivity_mask (array-like): the calculated conditional sensitivity mask with shape (Nx, Ny)

    """

    def __init__(self, xdata: Array, ydata: Array, xscaler_type: str='', yscaler_type: str=''):
        # Data array
        self.xdata = xdata
        self.ydata = ydata

        # Data dimensions
        assert xdata.shape[0] == ydata.shape[0], \
            "xdata and ydata must be the same number of samples"
        self.Ns = xdata.shape[0]
        self.Nx = xdata.shape[1]
        self.Ny = ydata.shape[1]

        # Create the transformer of the data
        self.xscaler_type = xscaler_type.lower()
        self.yscaler_type = yscaler_type.lower()
        self.xscaler = get_scaler(self.xdata, self.xscaler_type)
        self.yscaler = get_scaler(self.ydata, self.yscaler_type)

        # Data sensitivity
        self.sensitivity_config = {
            "method": None,
            "metric": None,
            "sst": None,
            "ntest": None,
            "alpha": None,
            "bins": None,
            "k": None,
            "n_jobs": None,
            "seed_shuffle": None,
        }
        self.sensitivity = np.zeros([self.Nx, self.Ny])
        self.sensitivity_mask = np.zeros([self.Nx, self.Ny], dtype='bool')
        self.cond_sensitivity_mask = np.zeros([self.Nx, self.Ny], dtype='bool')
        self.sensitivity_done = False
        self.loaded_from_other_sources = False
    

    def calculate_sensitivity(
        self, method: str='gsa', metric: str='it-bins', 
        sst: bool=False, ntest: int=100, alpha: float=0.05, 
        bins: int=10, k: int=5, n_jobs=-1, seed_shuffle: int=1234,
        verbose: int=0
    ):
        """Calculate the sensitivity between xdata and ydata.

        Args:
            method (str): The sensitivity methods, including:
                "gsa": the pairwise global sensitivity analysis
                "pc": a modified PC algorithm that include conditional indendpence test after gsa
                Defaults to 'mi-bins'.
            metric (str): The metric calculating the sensitivity, including:
                "it-bins": the information-theoretic measures (MI and CMI) using binning approach
                "it-knn": the information-theoretic measures (MI and CMI) using knn approach
                "corr": the correlation coefficient
                Defaults to 'corr'.
            sst (bool): whether to perform statistical significance test. Defaults to False.
            ntest (int): number of shuffled samples in sst. Defaults to 100.
            alpha (float): the significance level. Defaults to 0.05.
            bins (int): the number of bins for each dimension when metric == "it-knn". Defaults to 10.
            k (int): the number of nearest neighbors when metric == "it-knn". Defaults to 5.
            seed_shuffle (int): the random seed number for doing shuffle test. Defaults to 5.
            verbose (int): the verbosity level (0: normal, 1: debug). Defaults to 0.
        """
        sensitivity_config = self.sensitivity_config
        # xdata, ydata = self.xdata, self.ydata
        xdata_scaled, ydata_scaled = self.xdata_scaled, self.ydata_scaled
        # Calculate sensitivity
        sensitivity, sensitivity_mask, cond_sensitivity_mask = analyze_interdependency(
            xdata_scaled, ydata_scaled, method, metric, sst, 
            ntest, alpha, bins, k, n_jobs, seed_shuffle, verbose=verbose
        )

        # Update the configuration
        sensitivity_config['method'] = method
        sensitivity_config['metric'] = metric
        sensitivity_config['sst'] = sst
        sensitivity_config['ntest'] = ntest
        sensitivity_config['alpha'] = alpha
        sensitivity_config['bins'] = bins
        sensitivity_config['k'] = k
        sensitivity_config['n_jobs'] = n_jobs
        sensitivity_config['seed_shuffle'] = seed_shuffle
        self.sensitivity_config = sensitivity_config

        # Update the analysis result
        self.sensitivity_done = True
        self.sensitivity = sensitivity
        self.sensitivity_mask = sensitivity_mask
        self.cond_sensitivity_mask = cond_sensitivity_mask
    
    @property
    def xdata_scaled(self):
        return self.xscaler.transform(self.xdata)

    @property
    def ydata_scaled(self):
        return self.yscaler.transform(self.ydata)
    
    def save(self, rootpath: PosixPath=Path("./")):
        """Save data and sensitivity analysis results to specified location, including:
            - data (x, y) and scaler
            - sensitivity analysis configuration
            - sensitivity analysis results

        Args:
            rootpath (PosixPath): the root path where data will be saved

        """
        if not self.sensitivity_done:
            raise Exception("Sensitivity analysis is not done yet.")

        if not rootpath.exists():
            rootpath.mkdir(parents=True)

        # xdata and ydata
        f_x, f_y = rootpath / "x.npy", rootpath / "y.npy"
        np.save(f_x, self.xdata)
        np.save(f_y, self.ydata)

        # x and y scalers
        f_scaler = rootpath / "scaler.pkl"
        scaler = {"x": self.xscaler, "y": self.yscaler, 
                  "xtype": self.xscaler_type, "ytype": self.yscaler_type}
        with open(f_scaler, "wb") as f:
            pickle.dump(scaler, f)
        
        # sensitivity configurations
        f_sensitivity_config = rootpath / "sens_configs.json"
        with open(f_sensitivity_config, "w") as f:
            json.dump(self.sensitivity_config, f)

        # sensitivity results
        f_s = rootpath / "sensitivity.npy"
        f_mask = rootpath / "sensitivity_mask.npy"
        f_cond_mask = rootpath / "cond_sensitivity_mask.npy"
        np.save(f_s, self.sensitivity)
        np.save(f_mask, self.sensitivity_mask)
        np.save(f_cond_mask, self.cond_sensitivity_mask)
    
    def load(self, rootpath: PosixPath=Path("./"), check_xy: bool=True, overwrite: bool=False):
        """load data and sensitivity analysis results from specified location, including:
            - data (x, y) and scaler
            - sensitivity analysis configuration
            - sensitivity analysis results

        Args:
            rootpath (PosixPath): the root path where data will be loaded

        """
        if self.sensitivity_done and not overwrite:
            raise Exception("Sensitivity analysis has been performed.")
        
        # Load xdata and ydata
        f_x, f_y = rootpath / "x.npy", rootpath / "y.npy"
        xdata = np.load(f_x)
        ydata = np.load(f_y)
        if check_xy:
            assert np.allclose(xdata, self.xdata)
            assert np.allclose(ydata, self.ydata)
        self.xdata, self.ydata = xdata, ydata
        self.Ns = xdata.shape[0]
        self.Nx = xdata.shape[1]
        self.Ny = ydata.shape[1]

        # x and y scalers
        f_scaler = rootpath / "scaler.pkl"
        with open(f_scaler, "rb") as f:
            scaler = pickle.load(f)
        self.xscaler = scaler['x']
        self.yscaler = scaler['y']
        self.xscaler_type = scaler['xtype']
        self.yscaler_type = scaler['ytype']
        
        # sensitivity configurations
        f_sensitivity_config = rootpath / "sens_configs.json"
        with open(f_sensitivity_config, "r") as f:
            self.sensitivity_config = json.load(f)

        # sensitivity results
        f_s = rootpath / "sensitivity.npy"
        f_mask = rootpath / "sensitivity_mask.npy"
        f_cond_mask = rootpath / "cond_sensitivity_mask.npy"
        sensitivity = np.load(f_s)
        sensitivity_mask = np.load(f_mask)
        cond_sensitivity_mask = np.load(f_cond_mask)
        assert sensitivity.shape == (self.Nx, self.Ny)
        assert sensitivity_mask.shape == (self.Nx, self.Ny)
        assert cond_sensitivity_mask.shape == (self.Nx, self.Ny)
        self.sensitivity = sensitivity
        self.sensitivity_mask = sensitivity_mask
        self.cond_sensitivity_mask = cond_sensitivity_mask

        self.loaded_from_other_sources = True
        self.sensitivity_done = True
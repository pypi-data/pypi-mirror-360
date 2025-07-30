"""The general KIM class."""

# Author: Peishi Jiang <shixijps@gmail.com>

from .data import Data
from .mapping_model.loss_func import loss_mse
from .mapping_model import train_ensemble
from .mapping_model import MLP
from .utils import compute_metrics

import json
import random
import pickle
import itertools
from copy import deepcopy
from pathlib import PosixPath, Path

import jax
import jax.numpy as jnp
import numpy as np
import equinox as eqx

from jaxlib.xla_extension import Device
from typing import Optional
from jaxtyping import Array

# TODO: Need a great way to pass the computational device


class KIM(object):
    """The class for knowledge-informed mapping training, prediction, saving and loading.

    Arguments:
    ----------
    data (Data): the Data object containing the ensemble data and sensitivity analysis result.
    map_configs (dict): the mapping configuration, including all the arguments of Map class except x and y.
    mask_option (str): the masking option including 
                      - "sensitivity" (using data.sensitivity_mask), and 
                      - "cond_sensitivity" (using data.cond_sensitivity_mask).
    map_option (str): the map option including
                      - "many2one": knowledge-informed mapping using sensitivity analysis result as filter, and
                      - "many2many": normal mapping without being knowledge-informed
    other_mask (List): the additional mask to be assigned to self.mask with size Nx. Default to None.
    name (str): the name of the KIM object

    Attributes:
    ----------
    self.data (Data) : argument copy
    self.map_configs (dict) : argument copy
    self.map_option (str) : argument copy
    self.mask_option (str) : argument copy
    self.trained (bool) : whether KIM has been trained
    self.loaded_from_other_sources (bool) : whether KIM is loaded from other sources.
    self.Ns (int) : the number of ensemble members (from data.Ns)
    self.Nx (int) : the number of input features (from data.Nx)
    self.Ny (int) : the number of output features (from data.Ny)
    self.mask (Array) : the masked array with shape (Nx, Ny)
    self._n_maps (int) : the number of maps
    self._maps (int) : the trained maps

    """

    def __init__(
        self, data: Data, map_configs: dict, 
        mask_option: str='cond_sensitivity', 
        map_option: str='many2one',
        other_mask: Optional[Array]=None,
        name: str='kim'
    ):
        self.name = name
        # Check whether sensitivity has been performed in Data
        if not data.sensitivity_done and map_option == "many2one":
            raise Exception(
                "Sensitivity analysis has not been performed. So, KIM can not be executed in many to one mode."
            )
        self.data = data
        self.trained = False
        self.loaded_from_other_sources = False

        self.Ns, self.Nx, self.Ny = data.Ns, data.Nx, data.Ny
        self.mask_option = mask_option
        self.other_mask = other_mask
        if mask_option == "sensitivity":
            self.mask = data.sensitivity_mask
        elif mask_option == "cond_sensitivity":
            self.mask = data.cond_sensitivity_mask
        else:
            raise Exception("Unknown mask_option: %s" % mask_option)
        
        # Check whether additional masks are needed
        if self.other_mask is not None:
            assert len(self.other_mask) == self.Nx
            for i in range(self.Ny):
                self.mask[~self.other_mask,i] = False

        # Initialize variables/attributes for mappings
        if map_option == "many2one":
            n_maps = self.Ny
        elif map_option == "many2many":
            n_maps = 1 
        else:
            raise Exception("Unknown mapping option: %s" % map_option)
        self.map_configs = map_configs
        self.map_option = map_option
        self._n_maps = n_maps

    @property
    def maps(self):
        if self.trained:
            return self._maps
        else:
            print("KIM has not been trained yet.")

    @property
    def n_maps(self):
        return self._n_maps

    def train(self, verbose: int=0):
        # Initialize
        if self.map_option == "many2many":
            maps = self._init_map_many2many()
        elif self.map_option == "many2one":
            maps = self._init_map_many2one()
        # Train
        for one_map in maps:
            one_map.train(verbose=verbose)
        self._maps = maps
        self.trained = True
    
    def _init_map_many2many(self):
        x, y = self.data.xdata_scaled, self.data.ydata_scaled
        x, y = jnp.array(x), jnp.array(y)  # convert to jnp array
        map_configs = deepcopy(self.map_configs)
        one_map = Map(x, y, **map_configs)
        # one_map.train(verbose=0)
        return [one_map]

    def _init_map_many2one(self):
        if not self.data.sensitivity_done:
            raise Exception(
                "The sensitivity analysis is not done. \
                    We can't train the knowledge-informed mapping."
            )
        xall, yall = self.data.xdata_scaled, self.data.ydata_scaled
        mask_all = self.mask
        maps = []
        for i in range(self.n_maps):
            # Get the masked inputs and the outpus
            mask = mask_all[:,i]
            if mask.sum() == 0:
                print(f"There is no sensitive input to the {i} output.")
                one_map = None
            else:
                x, y = xall[:, mask], yall[:, [i]]
                x, y = jnp.array(x), jnp.array(y) # convert to jnp array
                # Initialize and train the mapping
                # print(self.map_configs, x.shape)
                map_configs = deepcopy(self.map_configs)
                one_map = Map(x, y, **map_configs)
            # one_map.train(verbose=0)
            maps.append(one_map)
        return maps
    
    def evaluate_maps_on_givendata(self):
        """Perform predictions on the given dataset
        """
        # TODO
        # Make the prediction
        y_ens, y_mean, y_mean_w, y_std_w, weights = self.predict(x=None)
        y_true = self.data.ydata

        # Separate them into trainining, validation, and test set
        if 'num_train_sample' in self.map_configs['dl_hp_fixed'] and \
           'num_val_sample' in self.map_configs['dl_hp_fixed']:
            Ns_train = self.map_configs['dl_hp_fixed']['num_train_sample']
            Ns_val = self.map_configs['dl_hp_fixed']['num_val_sample']
            sep1, sep2 = Ns_train, Ns_train+Ns_val
            y_ens_train, y_ens_val, y_ens_test = y_ens[:,:sep1,...], y_ens[:,sep1:sep2,...], y_ens[:,sep2:,...]
            y_true_train, y_true_val, y_true_test = y_true[:sep1,...], y_true[sep1:sep2,...], y_true[sep2:,...]
            y_mw_train, y_mw_val, y_mw_test = y_mean_w[:sep1,...], y_mean_w[sep1:sep2,...], y_mean_w[sep2:,...]
            y_stdw_train, y_stdw_val, y_stdw_test = y_std_w[:sep1,...], y_std_w[sep1:sep2,...], y_std_w[sep2:,...]
        elif 'num_train_sample' in self.map_configs['dl_hp_fixed'] and \
             'num_val_sample' not in self.map_configs['dl_hp_fixed']:
            Ns_train = self.map_configs['dl_hp_fixed']['num_train_sample']
            sep1 = Ns_train
            y_ens_train, y_ens_val, y_ens_test = y_ens[:,:sep1,...], None, y_ens[:,sep1:,...]
            y_true_train, y_true_val, y_true_test = y_true[:sep1,...], None, y_true[sep1:,...]
            y_mw_train, y_mw_val, y_mw_test = y_mean_w[:sep1,...], None, y_mean_w[sep1:,...]
            y_stdw_train, y_stdw_val, y_stdw_test = y_std_w[:sep1,...], None, y_std_w[sep1:,...]
        else:
            y_ens_train, y_ens_val, y_ens_test = y_ens, None, None
            y_true_train, y_true_val, y_true_test = y_true, None, None
            y_mw_train, y_mw_val, y_mw_test = y_mean_w, None
            y_stdw_train, y_stdw_val, y_stdw_test = y_std_w, None

        # Calculate the performance metrics
        Nens, Ny = y_ens.shape[0], self.Ny
        if 'num_train_sample' in self.map_configs['dl_hp_fixed'] and \
           'num_val_sample' in self.map_configs['dl_hp_fixed']:
            rmse_train, mkge_train = np.zeros([Nens,Ny]), np.zeros([Nens,Ny])
            rmse_val, mkge_val = np.zeros([Nens,Ny]), np.zeros([Nens,Ny])
            rmse_test, mkge_test = np.zeros([Nens,Ny]), np.zeros([Nens,Ny])
            for i in range(Nens):
                for j in range(Ny):
                    metrics = compute_metrics(y_ens_train[i,...,j], y_true_train[...,j])
                    rmse_train[i,j] = metrics['rmse']
                    mkge_train[i,j] = metrics['mkge']
                    metrics = compute_metrics(y_ens_val[i,...,j], y_true_val[...,j])
                    rmse_val[i,j] = metrics['rmse']
                    mkge_val[i,j] = metrics['mkge']
                    metrics = compute_metrics(y_ens_test[i,...,j], y_true_test[...,j])
                    rmse_test[i,j] = metrics['rmse']
                    mkge_test[i,j] = metrics['mkge']
        elif 'num_train_sample' in self.map_configs['dl_hp_fixed'] and \
             'num_val_sample' not in self.map_configs['dl_hp_fixed']:
            rmse_train, mkge_train = np.zeros([Nens,Ny]), np.zeros([Nens,Ny])
            rmse_val, mkge_val = None, None
            rmse_test, mkge_test = np.zeros([Nens,Ny]), np.zeros([Nens,Ny])
            for i in range(Nens):
                for j in range(Ny):
                    metrics = compute_metrics(y_ens_train[i,...,j], y_true_train[...,j])
                    rmse_train[i,j] = metrics['rmse']
                    mkge_train[i,j] = metrics['mkge']
                    metrics = compute_metrics(y_ens_test[i,...,j], y_true_test[...,j])
                    rmse_test[i,j] = metrics['rmse']
                    mkge_test[i,j] = metrics['mkge']
        else:
            rmse_train, mkge_train = np.zeros([Nens,Ny]), np.zeros([Nens,Ny])
            rmse_val, mkge_val = None, None
            rmse_test, mkge_test = None, None
            for i in range(Nens):
                for j in range(Ny):
                    metrics = compute_metrics(y_ens_train[i,...,j], y_true_train[...,j])
                    rmse_train[i,j] = metrics['rmse']
                    mkge_train[i,j] = metrics['mkge']

        ens_predict = {'train': y_ens_train, 'val': y_ens_val, 'test': y_ens_test}
        wm_predict = {'train': y_mw_train, 'val': y_mw_val, 'test': y_mw_test}
        wstd_predict = {'train': y_stdw_train, 'val': y_stdw_val, 'test': y_stdw_test}
        true = {'train': y_true_train, 'val': y_true_val, 'test': y_true_test}
        rmse = {'train': rmse_train, 'val': rmse_val, 'test': rmse_test}
        mkge = {'train': mkge_train, 'val': mkge_val, 'test': mkge_test}

        # Calculate bias and uncertainty
        wbias = {
            'train': np.mean(np.abs(y_true_train-y_mw_train), axis=0), 
            'val': np.mean(np.abs(y_true_val-y_mw_val), axis=0),
            'test': np.mean(np.abs(y_true_test-y_mw_test), axis=0)
        }
        wrelauncert = {
            'train': np.mean(y_stdw_train/y_true_train, axis=0), 
            'val': np.mean(y_stdw_val/y_true_val, axis=0),
            'test': np.mean(y_stdw_test/y_true_test, axis=0)
        }

        return {
            'ens predict': ens_predict,
            'weights': weights,
            'weighted mean predict': wm_predict,
            'weighted std predict': wstd_predict,
            'weighted bias': wbias,
            'weighted relative uncertainty': wrelauncert,
            'true': true,
            'rmse': rmse,
            'mkge': mkge
        }

    def predict(self, x: Optional[Array]=None):
        """Prediction using the trained KIM.

        Args:
            x (Array): predictors with shape (Ns,...,Nx)

        """
        if x is not None:
            assert x.shape[-1] == self.Nx  # The same dimension
            assert len(x.shape) >= 2  # At least 2 dimensions with the leading batch dimension
        else:
            x = self.data.xdata

        xraw = x
        xscaler, yscaler = self.data.xscaler, self.data.yscaler
        x = xscaler.transform(xraw)
        Ns = x.shape[0]

        n_ens = self.map_configs['n_model']
        Ny = self.Ny
        # n_maps = self.n_maps
        # xshape = list(x.shape)

        if self.map_option == "many2many":
            one_map = self._maps[0]
            y_ens, y_mean, y_mean_w, weights = one_map.predict(x)
            weights = np.stack([weights]*Ny, axis=-1)
        elif self.map_option == "many2one":
            y_ens, y_mean, y_mean_w, weights = [], [], [], []
            for i,one_map in enumerate(self._maps):
                one_mask = self.mask[:,i]
                if one_mask.sum() == 0:
                    assert one_map is None
                    y_e = np.empty([n_ens, Ns, 1]) + np.nan
                    w = np.empty([n_ens, Ns, 1]) + np.nan
                    y_m = np.empty([Ns, 1]) + np.nan
                    y_mw = np.empty([Ns, 1]) + np.nan
                else:
                    y_e, y_m, y_mw, w = one_map.predict(x[:, one_mask])
                    w = np.expand_dims(w, axis=-1)
                y_ens.append(np.array(y_e))
                y_mean.append(np.array(y_m))
                weights.append(np.array(w))
                y_mean_w.append(np.array(y_mw))
            y_ens = np.concat(y_ens, axis=-1)
            y_mean = np.concat(y_mean, axis=-1)
            y_mean_w = np.concat(y_mean_w, axis=-1)
            weights = np.concat(weights, axis=-1)

        # Scale back
        y_ens = np.array([yscaler.inverse_transform(y) for y in y_ens])
        y_mean = yscaler.inverse_transform(y_mean)
        y_mean_w= yscaler.inverse_transform(y_mean_w)

        # Calculate the weighted standard deviation
        def calculate_wstd(yens, ymw, w):
            return np.sqrt(np.average((yens-ymw)**2, weights=w, axis=0))
        # y_std_w = np.sqrt(np.average((y_ens-y_mean_w)**2, weights=weights, axis=0))
        y_std_w = []
        for i in range(weights.shape[-1]):
            yens, ymw, w = y_ens[...,i], y_mean_w[...,i], weights[...,i]
            y_std_w.append(calculate_wstd(yens, ymw, w))
        y_std_w = np.stack(y_std_w, axis=-1)
        # calculate_wstd = np.vectorize(calculate_wstd, signature='(m,n),(n),(m)->(n)')
        # y_std_w = calculate_wstd(y_ens, y_mean_w, weights)
        
        return y_ens, y_mean, y_mean_w, y_std_w, weights
        
    def save(self, rootpath: PosixPath=Path('./')):
        """Save the KIM, including:
            - the data object
            - all the mappings
            - the remaining configurations

        Args:
            rootpath (PosixPath): the root path where data will be saved

        """
        if not self.trained:
            raise Exception("KIM has not been trained yet.")

        if not rootpath.exists():
            rootpath.mkdir(parents=True)
        
        # Save the data object
        f_data = rootpath / "data"
        self.data.save(f_data)

        # Save all the mappings
        f_map_set = [rootpath / f'map{i}' for i in range(self._n_maps)]
        for i,one_map in enumerate(self._maps):
            one_map.save(f_map_set[i])

        # Save the remaining configurations
        f_configs = rootpath / "configs.pkl"
        configs = {
            "name": self.name,
            "map_configs": self.map_configs,
            "map_option": self.map_option,
            "n_maps": self._n_maps,
            "other_mask": self.other_mask
        }
        with open(f_configs, "wb") as f:
            pickle.dump(configs, f)

    def load(self, rootpath: PosixPath=Path("./")):
        """load the trained KIM from specified location.

        Args:
            rootpath (PosixPath): the root path where KIM will be loaded
        """
        # Load the overall configurations
        f_configs = rootpath / "configs.pkl"
        with open(f_configs, "rb") as f:
            configs = pickle.load(f)
        self.name = configs["name"]
        self.map_configs = configs["map_configs"]
        self.map_options = configs["map_option"]
        self._n_maps = configs["n_maps"]
        self.other_mask = configs["other_mask"]

        # Check whether additional masks are needed
        if self.other_mask is not None:
            assert len(self.other_mask) == self.Nx
            for i in range(self.Ny):
                self.mask[~self.other_mask,i] = False

        # Load the data object
        f_data = rootpath / "data"
        self.data.load(f_data, overwrite=True)
        self.Ns, self.Nx, self.Ny = self.data.Ns, self.data.Nx, self.data.Ny
        if self.mask_option == "sensitivity":
            self.mask = self.data.sensitivity_mask
        elif self.mask_option == "cond_sensitivity":
            self.mask = self.data.cond_sensitivity_mask
        else:
            raise Exception("Unknown mask_option: %s" % self.mask_option)

        # Load the trained mappings
        if self.map_option == "many2many":
            f_mapping = rootpath / 'map0'
            one_map = self._init_map_many2many()[0]
            one_map.load(f_mapping)
            maps = [one_map]
        elif self.map_option == "many2one":
            f_mapping_set = [rootpath / f'map{i}' for i in range(self._n_maps)]
            maps = self._init_map_many2one()
            for i,one_map in enumerate(maps):
                one_map.load(f_mapping_set[i])
        self._maps = maps

        self.trained = True
        self.loaded_from_other_sources = True


class Map(object):
    """The class for one mapping training, prediction, saving and loading.
       Ensemble training is supported through either serial or parallel way,
       using joblib.
       

    Arguments:
    ----------
    x (array-like): the predictors with shape (Ns, Nx)
    y (array-like): the predictands with shape (Ns, Ny)
    model_type (eqx._module._ModuleMeta): the equinox model class
    n_model (int): the number of ensemble models
    ensemble_type (str): the ensemble type, either 'single', 'serial' or 'parallel'.
    model_hp_choices (dict): the tunable model hyperparameters, in dictionary format 
        {key: [value1, value2,...]}. The model hyperparameters must follow the arguments
        of the specified model_type
    model_hp_fixed (dict): the fixed model hyperparameters, in dictionary format 
        {key: value}. The model hyperparameters must follow the arguments
        of the specified model_type
    optax_hp_choices (dict): the tunable optimizer hyperparameters, in dictionary format 
        {key: [value1, value2,...]}. The optimizer hyperparameters must follow the arguments
        of the specified optax optimizer. Key hyperparameters: 
        'optimizer_type' (str), 'nsteps' (int), and 'loss_func' (callable)
    optax_hp_fixed (dict): the fixed optimizer hyperparameters, in dictionary format 
        {key: value}. The optimizer hyperparameters must follow the arguments
        of the specified model_type. Key hyperparameters: 
        'optimizer_type' (str), 'nsteps' (int), and 'loss_func' (callable)
    dl_hp_choices (dict): the tunable dataloader hyperparameters, in dictionary format 
        {key: [value1, value2,...]}. The optimizer hyperparameters must follow the arguments
        of make_big_data_loader. Key hyperparameters: 'batch_size' (int) and 'num_train_sample' (int)
    dl_hp_fixed (dict): the fixed dataloader hyperparameters, in dictionary format 
        {key: value}. The optimizer hyperparameters must follow the arguments
        of make_big_data_loader. Key hyperparameters: 'batch_size' (int) and 'num_train_sample' (int
    training_parallel (bool): whether to perform parallel training
    ens_seed (Optional[int], optional): the random seed for generating ensemble configurations.
    parallel_config (Optional[dict], optional): the parallel training configurations following
        the arguments of joblib.Parallel
    device (Optional[Device], optional): the computing device to be set


    Attributes
    ----------
    self.x (array_like): argument copy
    self.y (array_like): argument copy
    self.n_model (int): argument copy
    self.training_parallel (bool) : argument copy
    self.model_type (eqx._module._ModuleMeta): argument copy
    self.ensemble_type (str): argument copy
    self.model_hp_choices (dict): argument copy
    self.model_hp_fixed (dict): argument copy
    self.optax_hp_choices (dict):argument copy
    self.optax_hp_fixed (dict): argument copy
    self.dl_hp_choices (dict): argument copy
    self.dl_hp_fixed (dict): argument copy
    self.training_parallel (bool): argument copy
    self.ens_seed (Optional[int], optional): argument copy
    self.parallel_config (Optional[dict], optional): argument copy
    self.device (Optional[Device], optional): argument copy
    self.trained (bool) : whether the mapping has been trained
    self.loaded_from_other_sources (bool) : whether the mapping is loaded from other sources.
    self.Ns (int): number of samples
    self.Nx (int): number of input features
    self.Ny (int): number of output features
    self.model_configs (list): model hyperparameters for all ensemble models
    self.optax_configs (list): optimizer hyperparameters for all ensemble models
    self.dl_configs (list): dataloader hyperparameters for all ensemble models
    self.model_ens (list): list of trained model ensemble
    self.loss_train_ens (list): list of the training losses over steps
    self.loss_val_ens (list): list of the val losses over steps

    """

    def __init__(
        self, x: Array, y: Array, model_type: eqx._module._ModuleMeta=MLP, 
        n_model: int=0, ensemble_type: str='single',
        model_hp_choices: dict={}, model_hp_fixed: dict={}, 
        optax_hp_choices: dict={}, optax_hp_fixed: dict={},
        dl_hp_choices: dict={}, dl_hp_fixed: dict={},
        training_parallel: bool=True,
        ens_seed: Optional[int]=None,
        parallel_config: Optional[dict]=None,
        device: Optional[Device]=None
    ):
        # TODO: Need a great way to pass the computational device
        # somehow coupled to the parallel training
        # for now, the parallel training uses joblib through multiple CPUs
        self.x, self.y = x, y
        self.training_parallel = training_parallel
        self.parallel_config = parallel_config
        self.device = device
        self.trained = False
        self.loaded_from_other_sources = False

        # Set up the random seed for ensemble generation
        random.seed(ens_seed)

        # Get the data dimensions
        assert self.x.shape[0] == self.y.shape[0]
        self.Ns, self.Nx, self.Ny = x.shape[0], x.shape[-1], y.shape[-1]
    
        # Get model configs
        self.model_type = model_type
        self.ensemble_type = ensemble_type
        self.model_hp_choices = model_hp_choices
        self.model_hp_fixed = model_hp_fixed
        self.optax_hp_choices = optax_hp_choices
        self.optax_hp_fixed = optax_hp_fixed
        self.dl_hp_choices = dl_hp_choices
        self.dl_hp_fixed = dl_hp_fixed
        self.n_model_init = n_model
        self._get_model_configs()

    @property
    def n_model(self):
        return len(self._model_configs)

    @property
    def model_configs(self):
        return self._model_configs

    @property
    def optax_configs(self):
        return self._optax_configs

    @property
    def dl_configs(self):
        return self._dl_configs

    @property
    def model_ens(self):
        if self.trained:
            return self._model_ens
        else:
            print("Mapping has not been trained yet.")

    @property
    def loss_train_ens(self):
        if self.trained:
            return self._loss_train_ens
        else:
            print("Mapping has not been trained yet.")

    @property
    def loss_val_ens(self):
        if self.trained:
            return self._loss_val_ens
        else:
            print("Mapping has not been trained yet.")

    def _get_model_configs(self):
        # Check key configs
        # TODO: A naming convention should be implemented in KIM.
        # e.g., the input and output parameters used in the DNN models.
        # Numbers of model inputs and outputs should be fixed
        if "in_size" in self.model_hp_choices:
            raise Exception("Input size should not be tunabled!")
        if "out_size" in self.model_hp_choices:
            raise Exception("Output size should not be tunabled!")
        if 'in_size' in self.model_hp_fixed and self.model_hp_fixed['in_size'] != self.Nx:
            raise Exception("Input size of the model is not: ", self.model_hp_fixed['in_size'])
        if 'out_size' in self.model_hp_fixed and self.model_hp_fixed['out_size'] != self.Ny:
            raise Exception("Output size of the model is not: ", self.model_hp_fixed['out_size'])
        self.model_hp_fixed['in_size'] = self.Nx
        self.model_hp_fixed['out_size'] = self.Ny

        if 'optimizer_type' not in self.optax_hp_fixed and \
            'optimizer_type' not in self.optax_hp_choices:
            self.optax_hp_fixed['optimizer_type'] = 'Adam'
        if 'nsteps' not in self.optax_hp_fixed and \
            'nsteps' not in self.optax_hp_choices:
            self.optax_hp_fixed['nsteps'] = 100
        if 'loss_func' not in self.optax_hp_fixed and \
            'loss_func' not in self.optax_hp_choices:
            self.optax_hp_fixed['loss_func'] = loss_mse

        if 'batch_size' not in self.dl_hp_fixed and \
            'batch_size' not in self.dl_hp_choices:
            self.dl_hp_fixed['batch_size'] = 32
        if 'num_train_sample' not in self.dl_hp_fixed and \
            'num_train_sample' not in self.dl_hp_choices:
            self.dl_hp_fixed['num_train_sample'] = self.Ns
        if 'num_val_sample' not in self.dl_hp_fixed and \
            'num_val_sample' not in self.dl_hp_choices:
            self.dl_hp_fixed['num_val_sample'] = self.Ns - self.dl_hp_fixed['num_train_sample']
        # if 'device' not in self.dl_hp_fixed:
        #     self.dl_hp_fixed['device'] = self.de

        # Generate ensemble configurations
        n_model, model_configs, optax_configs, dl_configs = generate_ensemble_configs(
            self.model_hp_choices, self.model_hp_fixed,
            self.optax_hp_choices, self.optax_hp_fixed,
            self.dl_hp_choices, self.dl_hp_fixed,
            self.n_model_init, self.ensemble_type,
        )
        # self.n_model = n_model
        self._model_configs = model_configs
        self._optax_configs = optax_configs
        self._dl_configs = dl_configs
        # _, self.model_configs = generate_ensemble_configs(
        #     self.model_hp_choices, self.model_hp_fixed, self.n_model, self.ensemble_type
        # )
        # _, self.optax_configs = generate_ensemble_configs(
        #     self.optax_hp_choices, self.optax_hp_fixed, self.n_model, self.ensemble_type
        # )
        # self.n_model, self.dl_configs = generate_ensemble_configs(
        #     self.dl_hp_choices, self.dl_hp_fixed, self.n_model, self.ensemble_type
        # )

    def train(self, verbose: int=0):
        """Mapping training.

        Args:
            verbose (int): the verbosity level (0: normal, 1: debug)
        """
        if self.trained:
            raise Exception("The mapping has already been trained!")

        model_ens, loss_train_ens, loss_val_ens = train_ensemble(
            self.x, self.y, self.model_type, 
            self.model_configs, self.optax_configs, self.dl_configs, 
            self.training_parallel, self.parallel_config, verbose
        )
        self._model_ens = model_ens
        self._loss_train_ens = loss_train_ens
        self._loss_val_ens = loss_val_ens
        self.trained = True

    def predict(self, x: Array):
        """Prediction using the trained mapping.

        Args:
            x (Array): predictors with shape (Ns,...,Nx)

        """
        assert x.shape[-1] == self.Nx  # The same dimension
        assert len(x.shape) >= 2  # At least 2 dimensions with the leading batch dimension

        # Perform predictions on all models
        y_ens = []
        for i in range(self.n_model):
            y = jax.vmap(self.model_ens[i])(x)
            y_ens.append(y)
        y_ens = jnp.array(y_ens)
        
        # Calculate mean
        y_mean = jnp.array(y_ens).mean(axis=0)
        # print(y_mean)

        # Calculate weighted mean based on loss
        # loss_ens = self.loss_val_ens if len(self.loss_val_ens)>0 else self.loss_train_ens
        loss_ens = self.loss_val_ens if self.loss_val_ens[0] is not None else self.loss_train_ens
        loss = jnp.array([l_all[-1] for l_all in loss_ens])
        weights = 1./loss / jnp.sum(1./loss)
        weighted_product = jax.vmap(lambda w, y: w*y, in_axes=(0,0))
        y_ens_w = weighted_product(weights, y_ens)
        y_mean_w = y_ens_w.sum(axis=0)

        return y_ens, y_mean, y_mean_w, weights

    def save(self, rootpath: PosixPath=Path("./")):
        """Save the trained mapping to specified location, including:
            - trained models
            - model/optax/dl configurations
            - loss values for both training and validation sets

        Args:
            rootpath (PosixPath): the root path where mappings will be saved

        """
        if not self.trained:
            raise Exception("Mapping has not been trained yet.")

        if not rootpath.exists():
            rootpath.mkdir(parents=True)

        # Dump overall configurations
        f_overall_configs = rootpath / "configs.pkl"
        overall_configs = {
            "n_model": self.n_model,
            "ensemble_type": self.ensemble_type,
            "training_parallel": self.training_parallel,
            "parallel_config": self.parallel_config,
            "device": self.device,
            "Ns": self.Ns, "Nx": self.Nx, "Ny": self.Ny,
            "model_type": self.model_type,
        }
        with open(f_overall_configs, "wb") as f:
            pickle.dump(overall_configs, f)

        # Dump each model, its configuration, and its loss values
        for i, model in enumerate(self.model_ens):
            model_dir = rootpath / str(i)
            if not model_dir.exists():
                model_dir.mkdir(parents=True)

            f_model = model_dir / "model.eqx"
            f_configs = model_dir / "configs.pkl"
            f_loss = model_dir / "loss.pkl"

            # Save the trained model
            model_configs = self.model_configs[i]
            save_model(f_model, model_configs, self.model_ens[i])

            # Save the configuration
            configs = {
                "model_configs": self.model_configs[i],
                "optax_configs": self.optax_configs[i],
                "dl_configs": self.dl_configs[i],
            }
            with open(f_configs, "wb") as f:
                pickle.dump(configs, f)

            # Save its loss values
            loss = {
                "train": self.loss_train_ens[i],
                "val": self.loss_val_ens[i]
            }
            with open(f_loss, "wb") as f:
                pickle.dump(loss, f)

    def load(self, rootpath: PosixPath=Path("./")):
        """load the trained mapping from specified location.

        Args:
            rootpath (PosixPath): the root path where mappings will be loaded
        """
        if self.trained:
            raise Exception("Mapping has already been trained.")

        # Load the overall configuration
        f_overall_configs = rootpath / "configs.pkl"
        with open(f_overall_configs, "rb") as f:
            overall_configs = pickle.load(f)
        n_model = overall_configs["n_model"]
        self.ensemble_type = overall_configs["ensemble_type"]
        self.training_parallel = overall_configs["training_parallel"]
        self.parallel_config = overall_configs["parallel_config"]
        self.device = overall_configs["device"]
        Ns, Nx, Ny = overall_configs["Ns"], overall_configs["Nx"], overall_configs["Ny"]
        self.model_type = overall_configs["model_type"]

        assert Nx == self.Nx
        assert Ny == self.Ny
        
        # Load each model, its configuration, and its loss values
        model_ens = []
        model_configs, optax_configs, dl_configs = [], [], []
        loss_train_ens, loss_val_ens = [], []
        for i in range(n_model):
            f_model = rootpath / str(i) / "model.eqx"
            f_configs = rootpath / str(i) / "configs.pkl"
            f_loss = rootpath / str(i) / "loss.pkl"

            # Save the trained model
            m = load_model(f_model, self.model_type)
            model_ens.append(m)

            # Save the configuration
            with open(f_configs, "rb") as f:
                configs = pickle.load(f)
            model_configs.append(configs["model_configs"])
            optax_configs.append(configs["optax_configs"])
            dl_configs.append(configs["dl_configs"])

            # Save its loss values
            with open(f_loss, "rb") as f:
                loss = pickle.load(f)
            loss_train_ens.append(loss["train"])
            loss_val_ens.append(loss["val"])

        self._model_ens = model_ens
        self._model_configs = model_configs
        self._optax_configs = optax_configs
        self._dl_configs = dl_configs
        self._loss_train_ens = loss_train_ens
        self._loss_val_ens = loss_val_ens

        self.loaded_from_other_sources = True
        self.trained = True


def generate_ensemble_configs(
    model_hp_choices: dict, model_hp_fixed: dict,
    optax_hp_choices: dict, optax_hp_fixed: dict,
    dl_hp_choices: dict, dl_hp_fixed: dict,
    n_model: int, ens_type: str,
):
    hp_all = [(model_hp_choices, model_hp_fixed), 
              (optax_hp_choices, optax_hp_fixed),
              (dl_hp_choices, dl_hp_fixed)]

    # Check there is no overlapped keys between hp_choices and hp_fixed
    for hp_choices, hp_fixed  in hp_all: 
        hp_keys1 = list(hp_choices.keys())
        hp_keys2 = list(hp_fixed.keys())
        assert all(i not in hp_keys1 for i in hp_keys2)
        for key, value in hp_choices.items():
            assert isinstance(value, list)
        for key, value in hp_fixed.items():
            assert isinstance(value, float) | isinstance(value, int) | \
                isinstance(value, str) | callable(value)

    # Generate the ensemble configs
    model_configs, optax_configs, dl_configs = [], [], []
    if ens_type == 'single':
        n_model = 1
        model_configs = [model_hp_fixed]
        optax_configs = [optax_hp_fixed]
        dl_configs = [dl_hp_fixed]

    elif ens_type == 'ens_random':
        # Get the configurations for each ensemble member
        for i in range(n_model):
            config_three = []
            for hp_choices, hp_fixed in hp_all:
                config = {}
                # Fixed configurations
                for key, value in hp_fixed.items():
                    config[key] = value
                # Tuned configurations
                for key, choices in hp_choices.items():
                    value = random.sample(choices, 1)[0]
                    config[key] = value
                config_three.append(config)
            model_configs.append(config_three[0])
            optax_configs.append(config_three[1])
            dl_configs.append(config_three[2])

    elif ens_type == 'ens_grid':
        # Get all the combinations of tuned configurations
        hp_choices_three = {
            **model_hp_choices, **optax_hp_choices, **dl_hp_choices
        }
        keys_c, options_c = zip(*hp_choices_three.items())
        combinations = list(itertools.product(*options_c))
        n_model = len(combinations)
        # Get the configurations for each ensemble member
        for i in range(n_model):
            config_three = []
            tuned_config = dict(zip(keys_c, combinations[i]))
            for hp_choices, hp_fixed in hp_all:
                config = {}
                # Fixed configurations
                for key, value in hp_fixed.items():
                    config[key] = value
                # Tuned configurations
                for key, choices in hp_choices.items():
                    config[key] = tuned_config[key]
                config_three.append(config)
            model_configs.append(config_three[0])
            optax_configs.append(config_three[1])
            dl_configs.append(config_three[2])

    else:
        raise Exception('Unknown ensemble type %s' % ens_type)
    
    return n_model, model_configs, optax_configs, dl_configs

def save_model(filename, hyperparams, model):
    with open(filename, "wb") as f:
        hyperparam_str = json.dumps(hyperparams)
        # hyperparam_str = json.dumps({})
        f.write((hyperparam_str + "\n").encode())
        eqx.tree_serialise_leaves(f, model)

def load_model(filename, model_type):
    with open(filename, "rb") as f:
        hyperparams = json.loads(f.readline().decode())
        # print("hyperparameters: ")
        # print(hyperparams)
        # print("Model type: ")
        # print(model_type)
        model = model_type(**hyperparams)
        return eqx.tree_deserialise_leaves(f, model)

# def generate_ensemble_configs(
#     hp_choices: dict, hp_fixed: dict, n_model: int, ens_type: str
# ):
#     # Check there is no overlapped keys between hp_choices and hp_fixed
#     hp_keys1 = list(hp_choices.keys())
#     hp_keys2 = list(hp_fixed.keys())
#     assert all(i not in hp_keys1 for i in hp_keys2)
#     for key, value in hp_choices.items():
#         assert isinstance(value, list)
#     for key, value in hp_fixed.items():
#         assert isinstance(value, float) | isinstance(value, int) | \
#             isinstance(value, str) | callable(value)

#     # Generate the ensemble configs
#     configs = []
#     if ens_type == 'single':
#         n_model = 1
#         configs = [hp_fixed]

#     elif ens_type == 'ens_random':
#         for i in range(n_model):
#             config = {}
#             # Fixed configurations
#             for key, value in hp_fixed.items():
#                 config[key] = value
#             # Tuned configurations
#             for key, choices in hp_choices.items():
#                 value = random.sample(choices, 1)[0]
#                 config[key] = value
#             configs.append(config)

#     elif ens_type == 'ens_grid':
#         # Get all the combinations of tuned configurations
#         keys_c, options_c = zip(*hp_choices.items())
#         combinations = list(itertools.product(*options_c))
#         n_model = len(combinations)
#         for i in range(n_model):
#             # Tuned configurations
#             config = dict(zip(keys_c, combinations[i]))
#             # Fixed configurations
#             for key, value in hp_fixed.items():
#                 config[key] = value
#             configs.append(config)

#     else:
#         raise Exception('Unknown ensemble type %s' % ens_type)
    
#     return n_model, configs
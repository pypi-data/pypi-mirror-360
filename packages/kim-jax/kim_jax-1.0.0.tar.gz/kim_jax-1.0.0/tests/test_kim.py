import jax
import jax.numpy as jnp
import jax.random as jrn
import numpy as np

import pprint
import shutil
import pytest
from pathlib import Path
from copy import deepcopy

from kim.map import KIM
from kim.data import Data
from kim.mapping_model import MLP2, MLP

Ns = 500
Ns_train = 250
Ns_val = 50
in_size = 12
out_size = 1
hidden_activation = 'sigmoid'
final_activation = 'leaky_relu'
seed = 1024
seed_predict = 3636
seed_dl = 10
seed_model = 100
seed_shuffle = 1234
training_verbose = 1

# Data configuration
data_params = {
    # "xscaler_type": "standard",
    # "yscaler_type": "standard",
    "xscaler_type": "",
    "yscaler_type": "",
}

# Sensitivity analysis configuration
sensitivity_params = {
    "method": "pc", "metric": "it-knn",
    "sst": True, "ntest": 100, "alpha": 0.05, "k": 3,
    "seed_shuffle": seed_shuffle,
}

# Mapping parameters for each test below
map_configs = {
    # "model_type": MLP2,
    "model_type": MLP,
    'n_model': 3,
    'ensemble_type': 'ens_random',
    'model_hp_choices': {
        "depth": [1,3,5,6],
        "width_size": [3,6,10]
    },
    'model_hp_fixed': {
        "hidden_activation": hidden_activation,
        "final_activation": final_activation,
        "model_seed": seed_model
    },
    'optax_hp_choices': {
        'learning_rate': [0.01, 0.005, 0.003],
    },
    'optax_hp_fixed': {
        'nsteps': 10,
        'optimizer_type': 'adam',
    },
    'dl_hp_choices': {
        'batch_size': [8, 16]
    },
    'dl_hp_fixed': {
        'dl_seed': seed_dl,
        'num_train_sample': Ns_train,
        'num_val_sample': Ns_val
    },
    'ens_seed': seed,
    'training_parallel': True,
    'parallel_config': {
        'n_jobs': 5, 
        'backend': 'loky',
        'verbose': 0
    },
    'device': None,
}

def get_samples():
    key = jrn.key(seed)
    x = jrn.uniform(key, shape=(Ns, in_size))
    y = []
    for i in range(out_size):
        ye = x[:,i]*2 + 3. * x[:,i+2]**2 + x[:,i+4]**3
        y.append(ye)
    y = jnp.stack(y, axis=-1)
    return x, y

def get_samples_predict():
    key = jrn.key(seed_predict)
    x = jrn.uniform(key, shape=(Ns, in_size))
    y = []
    for i in range(out_size):
        ye = x[:,i]*2 + 3. * x[:,i+2]**2 + x[:,i+4]**3
        y.append(ye)
    y = jnp.stack(y, axis=-1)
    return x, y

def test_init():
    x, y = get_samples()
    data = Data(x, y, **data_params)

    # This would fail because data sensitivity analysis is not performed
    with pytest.raises(Exception) as e_info:
        kim = KIM(data, map_configs, mask_option="cond_sensitivity", map_option='many2one')

    # Check some parameters
    kim = KIM(data, map_configs, map_option='many2many')
    assert kim.n_maps == 1

    #
    data.calculate_sensitivity(**sensitivity_params)
    kim = KIM(data, map_configs, mask_option="cond_sensitivity", map_option='many2one')
    # print(kim.mask)
    assert np.array_equal(kim.mask, data.cond_sensitivity_mask)
    assert kim.n_maps == out_size

def test_train_many2many():
    x, y = get_samples()
    data = Data(x, y, **data_params)
    kim = KIM(data, map_configs, map_option='many2many')

    kim.train()
    # print(data.xdata[:10])
    # print(data.xdata_scaled[:10])
    # print(data.xdata.mean(axis=0))
    # print(data.xdata_scaled.mean(axis=0))
    # print(data.xdata.std(axis=0))
    # print(data.xdata_scaled.std(axis=0))
    # print(kim)
    # print(kim.maps[0].loss_train_ens)
    # print(kim.maps[0].loss_val_ens)
    assert kim.n_maps == 1
    assert kim.n_maps == len(kim.maps)
    assert kim.maps[0].n_model == map_configs["n_model"]
    assert len(kim.maps[0].loss_train_ens[0]) == map_configs["optax_hp_fixed"]["nsteps"]
    assert len(kim.maps[0].loss_val_ens[-1]) == map_configs["optax_hp_fixed"]["nsteps"]

def test_train_many2one():
    x, y = get_samples()
    data = Data(x, y, **data_params)
    data.calculate_sensitivity(**sensitivity_params)

    kim = KIM(data, map_configs, mask_option="cond_sensitivity", map_option='many2one')
    kim.train()

    print(kim.maps[0].loss_train_ens)
    print(kim.maps[0].loss_val_ens)
    print(kim.maps[-1].loss_train_ens)
    print(kim.maps[-1].loss_val_ens)

    assert kim.n_maps == out_size
    assert kim.n_maps == len(kim.maps)
    assert kim.maps[0].n_model == map_configs["n_model"]
    assert len(kim.maps[0].loss_train_ens[0]) == map_configs["optax_hp_fixed"]["nsteps"]
    assert len(kim.maps[0].loss_val_ens[-1]) == map_configs["optax_hp_fixed"]["nsteps"]

def test_predict():
    # Training data
    x, y = get_samples()
    data = Data(x, y, **data_params)
    data.calculate_sensitivity(**sensitivity_params)

    print(data.cond_sensitivity_mask)
    print(data.sensitivity_mask)

    # Evaluation/prediction data
    xb, yb = get_samples_predict()

    # Initialize three diffferent KIMs
    n_model = map_configs['n_model']
    kim1 = KIM(data, map_configs, map_option='many2many')
    kim2 = KIM(data, map_configs, mask_option="sensitivity", map_option='many2one')
    kim3 = KIM(data, map_configs, mask_option="cond_sensitivity", map_option='many2one')

    # Train the mappings
    kim1.train()
    kim2.train()
    kim3.train()

    # print(kim1.maps[0].model_ens)
    # print("")
    # print(kim2.maps[0].model_ens)
    # print("")
    # print(kim3.maps[0].model_ens)

    # Predict
    def mse(y, ypred):
        return jnp.mean((y-ypred) ** 2)
    y_ens1, y_mean1, y_mean_w1, y_std_w1, weights1 = kim1.predict(xb)
    y_ens2, y_mean2, y_mean_w2, y_std_w2, weights2 = kim2.predict(xb)
    y_ens3, y_mean3, y_mean_w3, y_std_w3, weights3 = kim3.predict(xb)
    error1, error_w1 = mse(yb, y_mean1), mse(yb, y_mean_w1)
    error2, error_w2 = mse(yb, y_mean2), mse(yb, y_mean_w2)
    error3, error_w3 = mse(yb, y_mean3), mse(yb, y_mean_w3)
    print(error1, error2, error3, error_w1, error_w2, error_w3)
    # print(y_mean2)
    # print(y_mean3)

    assert weights1.shape == (n_model, kim1.n_maps)
    assert weights2.shape == (n_model, kim2.n_maps)
    assert weights3.shape == (n_model, kim3.n_maps)

    # I expect weighted predictions better than the normal average result
    assert error1 >= error_w1
    assert error2 >= error_w2
    assert error3 >= error_w3

    # I expect the best to worst mapping orders: kim3 --> kim2 --> kim1
    assert error1 >= error2
    assert error2 >= error3
    assert error_w1 >= error_w2
    assert error_w2 >= error_w3

def test_save_load():
    # Training data
    x, y = get_samples()
    data = Data(x, y, **data_params)
    data.calculate_sensitivity(**sensitivity_params)

    # Initialize three diffferent KIMs
    kim = KIM(data, map_configs, mask_option="cond_sensitivity", map_option='many2one')
    assert not kim.trained
    kim.train()

    # Save the model
    root_path = Path("./kim_save")
    kim.save(root_path)
    assert not kim.loaded_from_other_sources

    # Load the model
    kim2 = KIM(data, map_configs={})
    assert not kim2.trained
    kim2.load(root_path)

    assert kim2.loaded_from_other_sources
    assert kim2.trained
    assert kim2.map_configs == kim.map_configs

    # Evaluation/prediction data
    xb, yb = get_samples_predict()
    y_ens1, y_mean1, y_mean_w1, y_std_w1, weights1 = kim.predict(xb)
    y_ens2, y_mean2, y_mean_w2, y_std_w2, weights2 = kim2.predict(xb)

    assert np.array_equal(weights1.sum(axis=0), np.ones(kim.n_maps))
    assert np.array_equal(weights2.sum(axis=0), np.ones(kim2.n_maps))
    assert np.array_equal(y_ens1, y_ens2)
    assert np.array_equal(y_mean1, y_mean2)
    assert np.array_equal(y_mean_w1, y_mean_w2)

    # Remove the saving folder upon success
    shutil.rmtree(root_path)

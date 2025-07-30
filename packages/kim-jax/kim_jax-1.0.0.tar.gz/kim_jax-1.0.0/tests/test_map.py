import jax
import jax.numpy as jnp
import jax.random as jrn

import equinox as eqx

import numpy as np

import pprint
import shutil
from pathlib import Path
from copy import deepcopy

from kim.map import Map
from kim.mapping_model import MLP2

Ns = 120
Ns_train = 80
Ns_val = 20
in_size = 10
out_size = 2
hidden_activation = 'sigmoid'
final_activation = 'leaky_relu'
seed = 1024
seed_dl = 1
seed_model = 10
training_verbose = 1

# Mapping parameters for each test below
map_init_params_random = {
    'n_model': 3,
    'ensemble_type': 'ens_random',
    'model_hp_choices': {
        "depth": [1,3,5,6]
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
        'dl_seed': seed_dl
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

map_init_params_grid = deepcopy(map_init_params_random)
map_init_params_grid['ensemble_type'] = 'ens_grid'

map_train_single = deepcopy(map_init_params_random)
map_train_single['ensemble_type'] = 'single'
map_train_single['n_model'] = 1
map_train_single['training_parallel'] = False
map_train_single['optax_hp_fixed']['learning_rate'] = 0.01
map_train_single['model_hp_fixed']['depth'] = 2
map_train_single['dl_hp_fixed']['batch_size'] = 16
map_train_single['optax_hp_choices'] = {}
map_train_single['model_hp_choices'] = {}
map_train_single['dl_hp_choices'] = {}

map_train_serial = deepcopy(map_init_params_random)
map_train_serial['training_parallel'] = False
map_train_serial['dl_hp_fixed']['num_train_sample'] = Ns_train
map_train_serial['dl_hp_fixed']['num_val_sample'] = Ns_val

map_train_parallel = deepcopy(map_train_serial)
map_train_parallel['training_parallel'] = True

def get_samples():
    key = jrn.key(seed)
    x = jrn.uniform(key, shape=(Ns, in_size))
    y = []
    for i in range(out_size):
        ye = x[:,i]*2 + x[:,i+2]**2 + x[:,i+4]**3
        y.append(ye)
    y = jnp.stack(y, axis=-1)
    return x, y

def test_map_init_random():
    x, y = get_samples()
    kimap = Map(x, y, MLP2, **map_init_params_random)

    # print(kimap.model_configs)
    # print(kimap.optax_configs)
    # print(kimap.dl_configs)

    assert kimap.n_model == map_init_params_random['n_model']
    assert len(kimap.model_configs) == map_init_params_random['n_model']
    assert len(kimap.optax_configs) == map_init_params_random['n_model']
    assert len(kimap.dl_configs) == map_init_params_random['n_model']

def test_map_init_grid():
    x, y = get_samples()
    kimap = Map(x, y, MLP2, **map_init_params_grid)

    # print(kimap.n_model)
    # pprint.pprint(kimap.model_configs)

    assert len(kimap.model_configs) == kimap.n_model
    assert len(kimap.optax_configs) == kimap.n_model
    assert len(kimap.dl_configs) == kimap.n_model

def test_map_train_single():
    x, y = get_samples()
    kimap = Map(x, y, MLP2, **map_train_single)

    # pprint.pprint(kimap.optax_configs)

    assert not kimap.trained
    kimap.train()
    # pprint.pprint(kimap.loss_train_ens)
    # pprint.pprint(kimap.loss_test_ens)

    assert len(kimap.model_ens) == kimap.n_model
    assert len(kimap.loss_train_ens) == kimap.n_model
    assert kimap.loss_train_ens[0].size == kimap.optax_configs[0]['nsteps']

def test_map_train_serial():
    x, y = get_samples()
    kimap = Map(x, y, MLP2, **map_train_serial)

    # pprint.pprint(kimap.optax_configs)

    assert not kimap.trained
    kimap.train(training_verbose)
    # pprint.pprint(kimap.loss_train_ens)
    # pprint.pprint(kimap.loss_test_ens)

    assert len(kimap.model_ens) == kimap.n_model
    assert len(kimap.loss_train_ens) == kimap.n_model
    assert len(kimap.loss_val_ens) == kimap.n_model
    assert kimap.loss_train_ens[0].size == kimap.optax_configs[0]['nsteps']

def test_map_train_parallel():
    x, y = get_samples()
    kimap = Map(x, y, MLP2, **map_train_parallel)

    # pprint.pprint(kimap.optax_configs)

    assert not kimap.trained
    kimap.train(training_verbose)
    pprint.pprint(kimap.loss_train_ens)
    pprint.pprint(kimap.loss_val_ens)

    assert len(kimap.model_ens) == kimap.n_model
    assert len(kimap.loss_train_ens) == kimap.n_model
    assert len(kimap.loss_val_ens) == kimap.n_model
    assert kimap.loss_train_ens[0].size == kimap.optax_configs[0]['nsteps']

def test_map_predict():
    N_predict = 5
    x, y = get_samples()
    kimap = Map(x, y, MLP2, **map_train_parallel)

    assert not kimap.trained
    kimap.train(training_verbose)

    # key = jrn.key(100)
    # x_samples = jrn.uniform(key, shape=(N_predict, in_size))
    x_samples = x[-N_predict:]
    y_samples = y[-N_predict:]
    y_pred, y_mu, y_mu_w, weights = kimap.predict(x_samples)
    # print(y_pred)
    # print(y_mu.shape)
    # print(y_mu_w.shape)
    # print(y_samples.shape)

    def mse(y, ypred):
        return jnp.mean((y-ypred) ** 2)
    error = mse(y_samples, y_mu)
    error_w = mse(y_samples, y_mu_w)

    assert np.isclose(weights.sum(), 1.0)
    assert weights.shape[0] == kimap.n_model
    assert y_pred.shape[0] == kimap.n_model
    assert y_mu.shape[1:] == y.shape[1:]
    assert y_mu_w.shape[1:] == y.shape[1:]
    assert error_w < error

def test_map_save_load():
    x, y = get_samples()
    kimap = Map(x, y, MLP2, **map_train_parallel)

    assert not kimap.trained
    kimap.train(training_verbose)

    # Save the model 
    root_path = Path('./mapping')
    kimap.save(root_path)
    assert not kimap.loaded_from_other_sources

    # Load the model
    kimap2 = Map(x, y)
    assert not kimap2.trained
    kimap2.load(root_path)

    yp1, _, _, _ = kimap.predict(x)
    yp2, _, _, _ = kimap2.predict(x)
    # print(yp1.shape)
    # print(yp2.shape) 
    # print(jnp.all(d))

    assert kimap2.loaded_from_other_sources
    assert kimap2.trained
    assert kimap2.model_configs[-1] == kimap.model_configs[-1]
    assert kimap2.optax_configs[-1] == kimap.optax_configs[-1]
    assert kimap2.dl_configs[-1] == kimap.dl_configs[-1]
    assert jnp.array_equal(yp1, yp2)
    # assert eqx.tree_equal(kimap2.model_ens[-1], kimap.model_ens[-1])
    # assert eqx.tree_equal(kimap2.model_configs[-1], kimap.model_configs[-1])

    # Remove the saving folder upon success
    shutil.rmtree(root_path)

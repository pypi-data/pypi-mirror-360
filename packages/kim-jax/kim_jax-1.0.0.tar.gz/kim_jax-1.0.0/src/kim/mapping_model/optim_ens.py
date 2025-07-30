"""Functions for training ensemble mappings."""

# Author: Peishi Jiang <shixijps@gmail.com>

from copy import deepcopy

import optax
import equinox as eqx
from joblib import Parallel, delayed
from typing import List, Dict, Tuple, Optional
from jaxtyping import Array

# import ray
# from ray.util.joblib import register_ray

from .optim import train
# from .dataloader import make_big_data_loader
from .dataloader_torch import make_pytorch_data_loader

make_data_loader = make_pytorch_data_loader

def train_ensemble(
    x: Array, y: Array, model_type: eqx._module._ModuleMeta,
    model_config_ens: List[Dict], optax_config_ens: List[Dict], dl_config_ens: List[Dict], 
    training_parallel: bool=True, parallel_config: Optional[dict]=None,
    verbose: int=0,
) -> Tuple:
    """Train ensemble models.

    Args:
        x (Array): the input data with shape (Ns, Nx)
        y (Array): the output data with shape (Ns, Ny)
        model_type (eqx._module._ModuleMeta): the type of DNN model
        model_config_ens (List[Dict]): the model configurations specific to the selected model_type
        optax_config_ens (List[Dict]): the optimizer configurations specific to optax optimizers
        dl_config_ens (List[Dict]):  the dataloader configurations specific to the BatchedDL
        training_parallel (bool, optional): whether to perform parallel training. Defaults to True.
        parallel_config (Optional[dict], optional): the parallel computing configuration using joblib.Parallel. Defaults to None.
        verbose (int):  the verbosity level (0: normal, 1: debug)

    Returns:
        Tuple: the trained models, the loss values of the training and validation dataloaders
    """
    if training_parallel:
        model_ens, loss_train_ens, loss_val_ens = train_ensemble_parallel(
            x, y, model_type, model_config_ens, optax_config_ens, dl_config_ens,
            parallel_config, verbose
        )
    else:
        model_ens, loss_train_ens, loss_val_ens = train_ensemble_serial(
            x, y, model_type, model_config_ens, optax_config_ens, dl_config_ens,
            verbose
        )
    return model_ens, loss_train_ens, loss_val_ens


def train_ensemble_parallel(
    x: Array, y: Array, model_type: eqx._module._ModuleMeta,
    model_config_ens: List[Dict], optax_config_ens: List[Dict], 
    dl_config_ens: List[Dict], parallel_config: Dict, verbose: int
) -> Tuple:
    assert x.shape[0] == y.shape[0]
    assert len(model_config_ens) == len(optax_config_ens)
    assert len(dl_config_ens) == len(optax_config_ens)
    n_model = len(model_config_ens)
    
    print(f"\n Performing ensemble training in parallel with {n_model} model configurations...")
    print("")

    n_jobs = parallel_config['n_jobs'] if 'n_jobs' in parallel_config else -1
    backend = parallel_config['backend'] if 'backend' in parallel_config else 'loky'
    verbose = parallel_config['verbose'] if 'verbose' in parallel_config else 0

    # if backend == 'ray':
    #     ray.init(address='auto')
    #     register_ray()
    model_ens, loss_train_ens, loss_val_ens = zip(
        # *Parallel(n_jobs=n_jobs, backend=backend, verbose=verbose, pre_dispatch='1.5*n_jobs')(
        *Parallel(n_jobs=n_jobs, backend=backend, verbose=verbose)(
            delayed(train_each_model)(
                x, y, model_type, model_config_ens[i], optax_config_ens[i], dl_config_ens[i]
            ) for i in range(n_model)
        )
    )

    print("Training completes.")
    
    return model_ens, loss_train_ens, loss_val_ens


def train_ensemble_serial(
    x: Array, y: Array, model_type: eqx._module._ModuleMeta,
    model_config_ens: List[Dict], optax_config_ens: List[Dict], 
    dl_config_ens: List[Dict], verbose: int
) -> Tuple:
    print(x.devices())
    print(y.devices())
    assert x.shape[0] == y.shape[0]
    assert len(model_config_ens) == len(optax_config_ens)
    assert len(dl_config_ens) == len(optax_config_ens)
    n_model = len(model_config_ens)

    print(f"\n Performing ensemble training in serial with {n_model} model configurations...")
    print("")

    model_ens, loss_train_ens, loss_val_ens = [], [], []
    for i in range(n_model):
        model_config = model_config_ens[i]
        optax_config = optax_config_ens[i]
        dl_config = dl_config_ens[i]
        if verbose == 1:
            print(f"Model {i}")
            print("Model type: ", model_type)
            print("Model configuration: ", model_config)
            print("Optimizer configuration: ", model_config)
            print("Dataloader configuration: ", model_config)
        model, loss_train, loss_val = train_each_model(
            x, y, model_type, model_config, optax_config, dl_config
        )
        model_ens.append(model)
        loss_train_ens.append(loss_train)
        loss_val_ens.append(loss_val)
    
    print("Training completes.")

    return model_ens, loss_train_ens, loss_val_ens


def train_each_model(x, y, model_type, model_config, optax_config, dl_config):
    # Let's make copies. Don't want to mess up with the original configs.
    model_config = deepcopy(model_config)
    optax_config = deepcopy(optax_config)
    dl_config = deepcopy(dl_config)

    # Create the dataloader
    Ns = x.shape[0]
    Ns_train = dl_config.pop('num_train_sample')
    Ns_train = min(Ns_train, Ns)
    Ns_val = dl_config.pop('num_val_sample')
    Ns_val = min(Ns_val, Ns-Ns_train)
    # Ns_test = Ns - Ns_train - Ns_val
    xtrain, ytrain = x[:Ns_train], y[:Ns_train]
    # traindl = make_data_loader(xtrain, ytrain, **dl_config)
    traindl = make_data_loader(xtrain, ytrain, **dl_config)
    if Ns_val != 0:
        xval, yval = x[Ns_train:Ns_train+Ns_val], y[Ns_train:Ns_train+Ns_val]
        # xtest, ytest = x[Ns_train:], y[Ns_train:]
        valdl = make_data_loader(xval, yval, **dl_config)
    else:
        valdl = None

    # Create the optimizer
    def get_optimizer(optimizer_type):
        # TODO: more optimizers to be added from
        # https://optax.readthedocs.io/en/latest/api/optimizers.html
        if optimizer_type.lower() == 'adam':
            return optax.adam
        elif optimizer_type.lower() == 'adam':
            return optax.lbfgs
        else:
            raise Exception('Unknown optimizer type %s' % optimizer_type)
    optimizer_type = optax_config.pop('optimizer_type')
    nsteps = optax_config.pop('nsteps')
    loss_func = optax_config.pop('loss_func')
    optim = get_optimizer(optimizer_type)
    optim = optim(**optax_config)

    # Initialize the model
    model = model_type(**model_config)

    # Let's train the model
    model, loss_train, loss_val = train(
        model, nsteps, loss_func, optim, traindl, valdl
    )

    return model, loss_train, loss_val
    
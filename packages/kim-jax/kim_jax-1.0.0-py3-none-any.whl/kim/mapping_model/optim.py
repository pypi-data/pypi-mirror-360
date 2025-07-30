"""Functions for training one mapping."""

# Author: Peishi Jiang <shixijps@gmail.com>

from .dataloader import BatchedDL

import jax.numpy as jnp
import optax
import equinox as eqx
from tqdm import tqdm

from typing import Optional, Callable, Tuple
from jaxtyping import Array, PyTree


def train(
    model: eqx.Module, nsteps:int, loss_func: Callable, 
    optim: optax.GradientTransformation, 
    trainloader: BatchedDL, testloader: Optional[BatchedDL]=None
) -> Tuple[eqx.Module, Array, Array]:
    """Function to train one model/mapping.

    Args:
        model (eqx.Module): the eqx.Module model to be trained
        nsteps (int): the number of training steps
        loss_func (Callable): the loss function
        optim (optax.GradientTransformation): the optimizer
        trainloader (BatchedDL): the training dataloader
        testloader (Optional[BatchedDL], optional): the test dataloader. Defaults to None.

    Returns:
        model: the trained model
        loss_train_set: the loss values of the train set
        loss_test_set: the loss values of the test set
    """
    opt_state = optim.init(eqx.filter(model, eqx.is_array))

    loss_train_set, loss_test_set = [], []
    for step in tqdm(range(nsteps)):
        # Update the model on the training data
        model, opt_state, loss_value_train = train_each_step(
            model, trainloader, loss_func, optim, opt_state)

        # Evaluate the model on the test data
        if testloader is not None:
            loss_value_test = evaluate(model, testloader, loss_func)
            loss_train_set.append(loss_value_train)
            loss_test_set.append(loss_value_test)
        else:
            loss_train_set.append(loss_value_train)

        # print(
        #     f"The training loss of step {step}: {loss_value_train}."
        # )
    
    loss_train_set = jnp.array(loss_train_set)
    loss_test_set = jnp.array(loss_test_set) if testloader is not None else None
    
    return model, loss_train_set, loss_test_set
        

@eqx.filter_jit
def make_step(
    model: eqx.Module,
    opt_state: PyTree,
    x: Array,
    y: Array,
    loss_func: Callable,
    optim: optax.GradientTransformation,
):

    loss_value, grads = eqx.filter_value_and_grad(loss_func)(model, x, y)
    updates, opt_state = optim.update(grads, opt_state, model)
    model = eqx.apply_updates(model, updates)
    return model, opt_state, loss_value

# @eqx.filter_jit
def train_each_step(
    model: eqx.Module, trainloader: BatchedDL, loss_func: Callable,
    optim: optax.GradientTransformation, opt_state: PyTree,
):
    train_loss, k = 0, 0
    for i, (x, y) in enumerate(trainloader):
        x, y = jnp.array(x), jnp.array(y)
        model, opt_state, train_loss_each = make_step(
            model, opt_state, x, y, loss_func, optim
        )
        k += 1
        train_loss += train_loss_each
    train_loss /= k
    return model, opt_state, train_loss


def evaluate(model: eqx.Module, testloader: BatchedDL, loss_func: Callable):
    test_loss, k = 0, 0
    loss_func = eqx.filter_jit(loss_func)
    for i, (x, y) in enumerate(testloader):
        x, y = jnp.array(x), jnp.array(y)
        test_loss_each = loss_func(model, x, y)
        k += 1
        test_loss += test_loss_each
    test_loss /= k
    return test_loss


# @eqx.filter_jit
# def train_each_step(
#     model: eqx.Module, trainloader: Array, loss_func: Callable,
#     optim: optax.GradientTransformation, opt_state: PyTree,
# ):
#     def loss_func_batch(c, batch):
#         x, y = batch
#         loss_value, grads = eqx.filter_value_grad(loss_func)(model, x, y)
#         return c, [loss_value, grads]
#     _, results = jax.lax.scan(loss_func_batch, None, xs=trainloader)
#     loss_value = results[0].mean()
#     grads = jtu.tree_map(lambda x: x.mean(), results[1])
#     updates, opt_state = optim.update(grads, opt_state)
#     model = eqx.apply_updates(model, updates)
#     return model, opt_state, loss_value, grads


# @eqx.filter_jit
# def evaluate(model: eqx.Module, testloader: Array, loss_func: Callable):
#     def loss_func_batch(c, batch):
#         x, y = batch
#         loss_value = loss_func(model, x, y)
#         return c, loss_value
#     _, loss_value_test = jax.lax.scan(loss_func_batch, None, xs=testloader)
#     loss_value_test = loss_value_test.mean()
#     return loss_value_test

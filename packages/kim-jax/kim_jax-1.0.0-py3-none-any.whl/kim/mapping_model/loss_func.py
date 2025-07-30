"""Loss functions."""

# Author: Peishi Jiang <shixijps@gmail.com>

import jax
import jax.numpy as jnp
import equinox as eqx

from jaxtyping import Array

# @eqx.filter_jit
def loss_mse(model: eqx.Module, x: Array, y: Array):
    # Assume the first dimensions of x and y are the batch dimensions
    pred_y = jax.vmap(model)(x)
    return jnp.mean((y - pred_y) ** 2)

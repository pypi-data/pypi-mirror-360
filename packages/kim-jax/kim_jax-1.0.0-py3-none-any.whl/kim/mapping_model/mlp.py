"""Multilayer perceptron models."""

# Author: Peishi Jiang <shixijps@gmail.com>

import jax
import jax.random as jrandom
import jax.numpy as jnp

import equinox as eqx
from equinox.nn import Linear
from typing import Callable
from jaxtyping import Array


class MLP(eqx.Module):
    layers: tuple[Linear, ...]
    hidden_activation: Callable
    final_activation: Callable

    def __init__(
        self,
        in_size: int=2,
        out_size: int=1,
        width_size: int=3,
        depth: int=3,
        # key: PRNGKeyArray=jrandom.key(1024),
        model_seed: int=1024,
        hidden_activation: str='tanh',
        final_activation: str='tanh',
        **kwargs
    ):
        super().__init__(**kwargs)
        key = jrandom.key(model_seed)
        keys = jrandom.split(key, depth + 1)

        # Get the activation functions
        self.hidden_activation = get_activation(hidden_activation)
        self.final_activation = get_activation(final_activation)

        layers = []
        if depth == 0:
            layers.append(Linear(in_size, out_size, True, key=keys[0]))
        else:
            layers.append(Linear(in_size, width_size, True, key=keys[0]))
            for i in range(depth - 1):
                layers.append(Linear(width_size, width_size, True, key=keys[i + 1]))
            layers.append(Linear(width_size, out_size, True, key=keys[-1]))
        self.layers = tuple(layers)

    def __call__(self, x: Array) -> Array:
        for layer in self.layers[:-1]:
            x = layer(x)
            x = self.hidden_activation(x)
        x = self.layers[-1](x)
        x = self.final_activation(x)
        return x


class MLP2(eqx.Module):
    layers: tuple[Linear, ...]
    hidden_activation: Callable
    final_activation: Callable

    def __init__(
        self,
        in_size: int=2,
        out_size: int=1,
        depth: int=3,
        # key: PRNGKeyArray=jrandom.key(1024),
        model_seed: int=1024,
        hidden_activation: str='tanh',
        final_activation: str='tanh',
        **kwargs
    ):
        super().__init__(**kwargs)
        key = jrandom.key(model_seed)
        keys = jrandom.split(key, depth + 1)

        # Get the activation functions
        self.hidden_activation = get_activation(hidden_activation)
        self.final_activation = get_activation(final_activation)

        # Calculate the width sizes of hidden layers
        width_sizes = jnp.linspace(in_size, out_size, depth + 2).astype(int).tolist()

        layers = []
        if depth == 0:
            layers.append(Linear(in_size, out_size, True, key=keys[0]))
        else:
            for i in range(depth+1):
                in_s, out_s = width_sizes[i], width_sizes[i+1]
                layers.append(Linear(in_s, out_s, True, key=keys[i]))
        self.layers = tuple(layers)

    def __call__(self, x: Array) -> Array:
        for layer in self.layers[:-1]:
            x = layer(x)
            x = self.hidden_activation(x)
        x = self.layers[-1](x)
        x = self.final_activation(x)
        return x


def get_activation(activation: str='tanh'):
    if activation == 'tanh':
        return jax.nn.tanh

    elif activation == 'leaky_relu':
        return jax.nn.leaky_relu

    elif activation == 'sigmoid':
        return jax.nn.sigmoid

    elif activation == 'relu':
        return jax.nn.relu
    
    else:
        raise Exception('Unknown activation: %s' % activation)
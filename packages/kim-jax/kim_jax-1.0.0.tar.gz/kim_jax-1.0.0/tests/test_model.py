# import jax
import jax.random as jrn
import jax.numpy as jnp

import optax

from kim.mapping_model import MLP, MLP2, loss_mse
from kim.mapping_model import train, make_big_data_loader


Ns = 1000
Ns_test = 50
in_size = 10
out_size = 2
width_size = 7
depth = 6
hidden_activation = 'sigmoid'
final_activation = 'leaky_relu'

seed = 1024
key = jrn.key(seed)

key1, key2 = jrn.split(key)

def get_samples():
    x = jrn.uniform(key1, shape=(Ns, in_size))
    # y = jrn.uniform(key2, shape=(Ns, out_size))
    y = []
    for i in range(out_size):
        ye = x[:,i]*2 + x[:,i+2]**2 + x[:,i+4]**3
        y.append(ye)
    y = jnp.stack(y, axis=-1)
    return x, y

def get_samples_test():
    x = jrn.uniform(key2, shape=(Ns_test, in_size))
    # y = jrn.uniform(key2, shape=(Ns, out_size))
    y = []
    for i in range(out_size):
        ye = x[:,i]*2 + x[:,i+2]**2 + x[:,i+4]**3
        y.append(ye)
    y = jnp.stack(y, axis=-1)
    return x, y

def test_mlp():
    x, y = get_samples()
    model = MLP(
        in_size, out_size, width_size, depth, seed,
        hidden_activation, final_activation
    )
    loss = loss_mse(model, x, y)
    assert len(model.layers) == depth + 1
    assert ~jnp.all(jnp.isnan(loss))

def test_mlp2():
    x, y = get_samples()
    model = MLP2(
        in_size, out_size, depth, seed,
        hidden_activation, final_activation
    )
    loss = loss_mse(model, x, y)
    assert len(model.layers) == depth + 1
    assert ~jnp.all(jnp.isnan(loss))

def test_train_mlp():
    nsteps = 10
    learning_rate = 0.001
    batch_size = 64

    optim = optax.adam(learning_rate=learning_rate)

    x_train, y_train = get_samples()
    x_test, y_test = get_samples_test()

    model = MLP2(
        in_size, out_size, depth, seed,
        hidden_activation, final_activation
    )
    
    train_dl = make_big_data_loader(x_train, y_train, batch_size=batch_size)
    test_dl = make_big_data_loader(x_test, y_test, batch_size=batch_size)

    # for x, y in train_dl:
    #     print(x.shape, y.shape)

    model, loss_train, loss_test = train(
        model, nsteps, loss_mse, optim, train_dl, test_dl
    )
    print(loss_train)
    print(loss_test)
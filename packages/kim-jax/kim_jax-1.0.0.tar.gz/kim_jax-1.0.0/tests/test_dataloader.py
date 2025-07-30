from kim.mapping_model.dataloader import make_big_data_loader, DataSet

import jax
import jax.numpy as jnp
import jax.random as jrn

seed = 1024
key = jrn.key(seed)
Nsx = 12
Nsy = 10
Nx = 5
Ny = 2

device = jax.devices()[0]

def get_samples():
    key1, key2 = jrn.split(key)
    x = jrn.uniform(key1, shape=(Nsx, Nx))
    y = jrn.uniform(key2, shape=(Nsy, Ny))
    return x, y

def test_data_set():
    x, y = get_samples()

    dataset1 = DataSet(x=x, y=y, seed=seed, device=device)
    dataset2 = DataSet(x=x, y=y, seed=None, device=device)

    idx1 = dataset1.idx
    idx2 = dataset2.idx

    assert ~jnp.all(idx1[:dataset1.n] == jnp.arange(dataset1.n)+dataset1.n_stack)
    assert jnp.all(idx2[:dataset2.n] == jnp.arange(dataset2.n)+dataset2.n_stack)

    # print(idx1)
    # print(idx2)
    # print(dataset2.n, dataset2.n_stack)

    x1, y1 = next(dataset1)
    x2, y2 = next(dataset2)

    assert x1.shape == ((Nsx-Nsy+1)*Nx,)
    assert x2.shape == ((Nsx-Nsy+1)*Nx,)
    assert y1.shape == (Ny,)
    assert y2.shape == (Ny,)

def test_dataloader1():
    test_batch = 2
    batch_size = 3

    x, y = get_samples()

    dl = make_big_data_loader(
        x=x, y=y, statics=None, chunk_size=12, n_hist=0, n_fut=0,
        batch_size=batch_size, dl_seed=None, device=device
    )

    for i, (bx,by) in enumerate(dl):
        # print(bx.shape)
        # print(by.shape)
        if i == test_batch:
            assert jnp.all(bx == x[i*batch_size:(i+1)*batch_size,:])
            assert jnp.all(by == y[i*batch_size:(i+1)*batch_size,:])
        # print(i)
        # assert jnp.all(bx == x[i*batch_size:(i+1)*batch_size,:])
        # assert jnp.all(by == y[i*batch_size:(i+1)*batch_size,:])
        # print(bx.shape)
        # print(by.shape)

def test_dataloader2():
    test_batch = 2
    batch_size = 1

    x, y = get_samples()

    dl = make_big_data_loader(
        x=x, y=y, statics=None, chunk_size=12, n_hist=0, n_fut=0,
        batch_size=batch_size, dl_seed=1024, device=device
    )

    for i, (bx,by) in enumerate(dl):
        print(bx.shape)
        if i == test_batch:
            assert ~jnp.all(bx == x[i*batch_size:(i+1)*batch_size,:])
            assert ~jnp.all(by == y[i*batch_size:(i+1)*batch_size,:])
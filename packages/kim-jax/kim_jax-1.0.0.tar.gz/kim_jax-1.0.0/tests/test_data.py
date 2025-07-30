import shutil
from pathlib import Path

import numpy as np

from kim import Data

np.random.seed(1)

Ns = 100
Nz = 3
metric='it-bins'
sst=True
ntest=100 
alpha=0.05 
bins=10
k=5
seed_shuffle = 998
xscaler_type='minmax'
yscaler_type='minmax'
verbose=1

def get_samples_1():
    xdata = np.arange(Ns)
    ydata = np.arange(Ns)
    return xdata, ydata

def get_samples_2():
    xdata = np.arange(Ns)
    ydata = np.arange(Ns)
    ydata[[10,20,30,40,50]] = 80
    return xdata, ydata

def get_samples_3():
    data = np.random.uniform(size=(Ns,2))
    x, y = data[:,0], data[:,1]
    return x, y

def get_samples_4():
    x = np.linspace(0, 1, Ns)
    y = x**2 + 2*x + 3
    return x, y

def get_samples_cond_1():
    zdata = np.random.random(size=(Ns,Nz))
    x= np.random.random(Ns) + np.dot(zdata, np.arange(Nz)) + 3
    y= np.random.random(Ns) + np.sum(zdata, axis=-1) + 5
    # y= np.random.random(Ns) + 5
    return x, y, zdata

def get_samples_cond_2():
    zdata = np.random.random(size=(Ns,Nz))
    x= np.random.random(Ns) + np.dot(zdata, np.arange(Nz)) + 3
    y= np.random.random(Ns) + x
    return x, y, zdata

def test_Data_gsa():
    x1, y1 = get_samples_1()
    x2, y2 = get_samples_2()
    x3, y3 = get_samples_3()
    x4, y4 = get_samples_4()
    xdata = np.array([x1, x2, x3, x4]).T
    ydata = np.array([y1, y2, y3, y4]).T

    data = Data(xdata, ydata, xscaler_type=xscaler_type, yscaler_type=yscaler_type)
    
    assert data.Ns == Ns
    assert data.Nx == 4
    assert data.Ny == 4

    data.calculate_sensitivity(
        'gsa', metric, sst, ntest, alpha, k=k, seed_shuffle=seed_shuffle, verbose=verbose
    )

    assert data.sensitivity_config['method'] == 'gsa'
    assert not data.sensitivity_mask[2,2]
    assert data.sensitivity_mask[-1,-1]
    assert data.sensitivity_mask[0,0]

    # print(data.sensitivity)
    # print(data.sensitivity_mask)

def test_Data_pc():
    x1, y1, cdata1 = get_samples_cond_1()
    x2, y2, cdata2 = get_samples_cond_2()
    xdata = np.array([x1, x2]).T
    xdata = np.concat([xdata, cdata1, cdata2], axis=1)
    ydata = np.array([y1, y2]).T

    data = Data(xdata, ydata, xscaler_type=xscaler_type, yscaler_type=yscaler_type)
    
    assert data.Ns == Ns
    assert data.Nx == 8
    assert data.Ny == 2

    data.calculate_sensitivity(
        'pc', metric, sst, ntest, alpha, k=k, seed_shuffle=seed_shuffle, verbose=verbose
    )

    # print(data.cond_sensitivity_mask)
    # print(data.sensitivity)
    assert data.sensitivity_config['method'] == 'pc'
    assert data.sensitivity_mask[1,1]
    assert data.sensitivity_mask.sum() > data.cond_sensitivity_mask.sum()

def test_Data_save_load():
    x1, y1, cdata1 = get_samples_cond_1()
    x2, y2, cdata2 = get_samples_cond_2()
    xdata = np.array([x1, x2]).T
    xdata = np.concat([xdata, cdata1, cdata2], axis=1)
    ydata = np.array([y1, y2]).T

    root_path = Path("./data")
    data = Data(xdata, ydata, xscaler_type=xscaler_type, yscaler_type=yscaler_type)
    data.calculate_sensitivity(
        'pc', metric, sst, ntest, alpha, k=k, seed_shuffle=seed_shuffle, verbose=verbose
    )
    data.save(root_path)

    data2 = Data(xdata, ydata)
    data2.load(root_path, check_xy=True)

    assert data2.sensitivity_config == data.sensitivity_config
    assert np.array_equal(data.sensitivity, data2.sensitivity)
    assert np.array_equal(data.sensitivity_mask, data2.sensitivity_mask)
    assert np.array_equal(data.cond_sensitivity_mask, data2.cond_sensitivity_mask)

    # Remove the saving folder upon success
    shutil.rmtree(root_path)
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from kim.utils.scaler import get_scaler

np.random.seed(1)

Ns = 100
Nz = 3
xscaler_type='minmax'
yscaler_type='minmax'

def get_samples():
    data = np.random.random(size=(Ns, Nz))
    return data

def test_identityscaler():
    data = get_samples() 
    scaler = get_scaler(scaler_type='')

    data_scaled = scaler.transform(data)
    data_scaledback = scaler.inverse_transform(data_scaled)

    assert np.all(data==data_scaled)    
    assert np.all(data_scaledback==data_scaled)    

def test_logscaler():
    data = get_samples() 
    scaler = get_scaler(scaler_type='log')

    data_scaled = scaler.transform(data)
    data_scaledback = scaler.inverse_transform(data_scaled)

    assert np.all(data_scaled == np.log(data) / np.log(scaler.base))    
    assert np.allclose(data_scaledback, data)    

def test_minmaxscaler():
    data = get_samples() 
    scaler = get_scaler(data, scaler_type='minmax')
    data_scaled = scaler.transform(data)
    data_scaledback = scaler.inverse_transform(data_scaled)

    scaler_true = MinMaxScaler()
    scaler_true.fit(data)
    data_scaled_true = scaler_true.transform(data)
    data_scaledback_true = scaler_true.inverse_transform(data_scaled)

    assert np.all(data_scaled == data_scaled_true)    
    assert np.all(data_scaledback == data_scaledback_true)    
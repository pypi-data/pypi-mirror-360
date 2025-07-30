"""A couple of utility functions and classes."""

# Author: Peishi Jiang <shixijps@gmail.com>

import numpy as np
from sklearn.preprocessing import StandardScaler, Normalizer, MinMaxScaler


def get_scaler(data=None, scaler_type=''):
    """Get the data scaler.

    Args:
        data (array-like or None): the data array with shape (Ns, Nx)
        scaler_type (str): the type of xdata scaler, either 'minmax', 'normalize', 'standard', 'log', or ''
    """
    if scaler_type == 'normalize':
        scaler = Normalizer()
        scaler.fit(data)
        return scaler

    elif scaler_type == 'minmax':
        scaler = MinMaxScaler()
        scaler.fit(data)
        return scaler

    elif scaler_type == 'standard':
        scaler = StandardScaler()
        scaler.fit(data)
        return scaler
    
    elif scaler_type == 'log':
        return LogScaler()

    elif scaler_type == '':
        return IdentifyScaler()
    
    else:
        raise Exception("Unknown scaler type: %s" % scaler_type)


class Scaler(object):
    """A scaler object with similar structure to the sklearn.preprocessing scalers.

    Arguments:
    ----------
    data (array-like or None): the data array

    Attributes
    ----------
    self.xdata (array-like): the copy of xdata

    """

    def __init__(self, data=None):
        self.data = data

    def fit(self, data):
        pass

    def transform(self, data):
        pass

    def inverse_transform(self, data):
        pass


class IdentifyScaler(Scaler):
    """The scaler performs nothing."""

    def transform(self, data):
        return data

    def inverse_transform(self, data):
        return data


class LogScaler(Scaler):
    """The scaler perform the logrithmic transformation."""

    def __init__(self, data=None, base=10.):
        super().__init__(data)
        self.base = base

    def transform(self, data):
        return np.log(data) / np.log(self.base)

    def inverse_transform(self, data):
        return np.power(self.base, data)
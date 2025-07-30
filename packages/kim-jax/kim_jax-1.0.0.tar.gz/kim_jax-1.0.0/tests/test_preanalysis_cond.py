import numpy as np
# from numpy.testing import assert_allclose

from kim.pre_analysis.metric_calculator import get_metric_calculator
from kim.pre_analysis.sst import shuffle_test
from kim.pre_analysis import pc

np.random.seed(1)

Ns = 1000
Nz = 3

def get_samples_1():
    zdata = np.random.random(size=(Ns,Nz))
    x= np.random.random(Ns) + np.dot(zdata, np.arange(Nz)) + 3
    y= np.random.random(Ns) + np.sum(zdata, axis=-1) + 5
    # y= np.random.random(Ns) + 5
    return x, y, zdata

def get_samples_2():
    zdata = np.random.random(size=(Ns,Nz))
    x= np.random.random(Ns) + np.dot(zdata, np.arange(Nz)) + 3
    y= np.random.random(Ns) + x
    return x, y, zdata

def test_parcorrcoef():
    x1, y1, cdata1 = get_samples_1()
    x2, y2, cdata2 = get_samples_2()

    _, cond_metric_calculator = get_metric_calculator("corr")
    m1 = cond_metric_calculator(x1, y1, cdata1)
    m2 = cond_metric_calculator(x2, y2, cdata2)

    assert m2 > m1

def test_cmibins():
    x1, y1, cdata1 = get_samples_1()
    x2, y2, cdata2 = get_samples_2()

    _, cond_metric_calculator = get_metric_calculator("it-bins", bins=10)
    m1 = cond_metric_calculator(x1, y1, cdata1)
    m2 = cond_metric_calculator(x2, y2, cdata2)

    assert m2 > m1

def test_cmiknn():
    x1, y1, cdata1 = get_samples_1()
    x2, y2, cdata2 = get_samples_2()

    _, cond_metric_calculator = get_metric_calculator("it-knn", k=3)
    m1 = cond_metric_calculator(x1, y1, cdata1)
    m2 = cond_metric_calculator(x2, y2, cdata2)

    assert m2 > m1

def test_cond_sst():
    x1, y1, cdata1 = get_samples_1()
    x2, y2, cdata2 = get_samples_2()

    _, cond_metric_calculator = get_metric_calculator("it-knn", k=3)
    m1, sig1 = shuffle_test(x1, y1, cond_metric_calculator, cdata=cdata1, ntest=100, alpha=0.05)
    m2, sig2 = shuffle_test(x2, y2, cond_metric_calculator, cdata=cdata2, ntest=100, alpha=0.05)

    assert not sig1
    assert sig2
    assert m2 > m1

def test_pc():
    x1, y1, cdata1 = get_samples_1()
    x2, y2, cdata2 = get_samples_2()
    xdata = np.array([x1, x2]).T
    xdata = np.concat([xdata, cdata1, cdata2], axis=1)
    ydata = np.array([y1, y2]).T

    print(xdata.shape, ydata.shape)
    # metric_calculator, cond_metric_calculator = get_metric_calculator("it-knn", k=5)
    metric_calculator, cond_metric_calculator = get_metric_calculator("corr")

    sensitivity, sensitivity_mask, cond_sensitivity_mask = pc(
        xdata, ydata, metric_calculator, cond_metric_calculator, 
        ntest=100, alpha=0.05)
    
    # print(sensitivity)
    # print(sensitivity_mask)
    # print(cond_sensitivity_mask)
    assert sensitivity_mask[1,1]
    assert sensitivity_mask.sum() > cond_sensitivity_mask.sum()
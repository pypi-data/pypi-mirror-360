import numpy as np
from numpy.testing import assert_allclose

from kim.pre_analysis.metric_calculator import get_metric_calculator
from kim.pre_analysis.sst import shuffle_test
from kim.pre_analysis import pairwise_analysis

np.random.seed(1)

def get_samples_1():
    xdata = np.array([1, 2, 3, 4, 5])
    ydata = np.array([1, 2, 3, 4, 5])
    return xdata, ydata

def get_samples_2():
    xdata = np.array([1, 2, 3, 4, 5])
    ydata = np.array([1, 2, 5, 4, 9])
    return xdata, ydata

def get_samples_3():
    data = np.random.uniform(size=(100,2))
    x, y = data[:,0], data[:,1]
    return x, y

def get_samples_4():
    x = np.linspace(0, 1, 100)
    y = x**2 + 2*x + 3
    return x, y

def test_corrcoef():
    x1, y1 = get_samples_1()
    x2, y2 = get_samples_2()

    metric_calculator, _ = get_metric_calculator("corr")
    m1 = metric_calculator(x1, y1)
    m2 = metric_calculator(x2, y2)

    assert_allclose(m1, 1, atol=1e-07)
    assert m2 < m1

def test_mibins():
    x1, y1 = get_samples_3()
    x2, y2 = get_samples_4()

    metric_calculator, _ = get_metric_calculator("it-bins", bins=10)
    m1 = metric_calculator(x1, y1)
    m2 = metric_calculator(x2, y2)

    assert m2 > m1

def test_miknn():
    x1, y1 = get_samples_3()
    x2, y2 = get_samples_4()

    metric_calculator, _ = get_metric_calculator("it-knn", k=3)
    m1 = metric_calculator(x1, y1)
    m2 = metric_calculator(x2, y2)

    assert m2 > m1

def test_sst():
    x1, y1 = get_samples_3()
    x2, y2 = get_samples_4()
    metric_calculator, _ = get_metric_calculator("it-knn", k=3)
    m1, sig1 = shuffle_test(x1, y1, metric_calculator, cdata=None, ntest=100, alpha=0.05)
    m2, sig2 = shuffle_test(x2, y2, metric_calculator, cdata=None, ntest=100, alpha=0.05)
    assert not sig1
    assert sig2

def test_pairwise_analysis():
    x1, y1 = get_samples_3()
    x2, y2 = get_samples_4()
    xdata = np.array([x1, x2]).T
    ydata = np.array([y1, y2]).T

    metric_calculator, _ = get_metric_calculator("it-knn", k=3)

    sensitivity, sensitivity_mask = pairwise_analysis(
        xdata, ydata, metric_calculator, 
        sst=True, ntest=100, alpha=0.05)
    
    # print(sensitivity_mask)
    # print(sensitivity)
    assert sensitivity_mask[1,1]
    assert not sensitivity_mask[0,0]
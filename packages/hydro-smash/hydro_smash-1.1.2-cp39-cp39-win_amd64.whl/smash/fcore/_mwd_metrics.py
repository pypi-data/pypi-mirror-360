"""
Module mwd_metrics


Defined at ../smash/fcore/signal_analysis/mwd_metrics.f90 lines 20-265

(MWD) Module Wrapped and Differentiated.

Subroutine
----------

- kge_components

Function
--------

- nse
- nnse
- kge
- mae
- mape
- se
- mse
- rmse
- lgrm
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

def nse(x, y):
    """
    res = nse(x, y)
    
    
    Defined at ../smash/fcore/signal_analysis/mwd_metrics.f90 lines 24-59
    
    Parameters
    ----------
    x : float array
    y : float array
    
    Returns
    -------
    res : float
    
    Notes
    -----
    
    NSE computation function
    
    Given two single precision array(x, y) of dim(1) and size(n),
    it returns the result of NSE computation
    num = sum(x**2) - 2 * sum(x*y) + sum(y**2)
    den = sum(x**2) - n * mean(x) ** 2
    NSE = 1 - num / den
    NSE numerator / denominator
    NSE criterion
    only: sp
    """
    res = _libfcore.f90wrap_mwd_metrics__nse(x=x, y=y)
    return res

def nnse(x, y):
    """
    res = nnse(x, y)
    
    
    Defined at ../smash/fcore/signal_analysis/mwd_metrics.f90 lines 61-73
    
    Parameters
    ----------
    x : float array
    y : float array
    
    Returns
    -------
    res : float
    
    Notes
    -----
    
    Normalized NSE(NNSE) computation function
    
    Given two single precision array(x, y) of dim(1) and size(n),
    it returns the result of NSE computation
    NSE = 1 / (2 - NSE)
    """
    res = _libfcore.f90wrap_mwd_metrics__nnse(x=x, y=y)
    return res

def kge_components(x, y, r, a, b):
    """
    kge_components(x, y, r, a, b)
    
    
    Defined at ../smash/fcore/signal_analysis/mwd_metrics.f90 lines 75-116
    
    Parameters
    ----------
    x : float array
    y : float array
    r : float
    a : float
    b : float
    
    Notes
    -----
    
    KGE components computation subroutine
    
    Given two single precision array(x, y) of dim(1) and size(n),
    it returns KGE components r, a, b
    r = cov(x,y) / std(y) / std(x)
    a = mean(y) / mean(x)
    b = std(y) / std(x)
    """
    _libfcore.f90wrap_mwd_metrics__kge_components(x=x, y=y, r=r, a=a, b=b)

def kge(x, y):
    """
    res = kge(x, y)
    
    
    Defined at ../smash/fcore/signal_analysis/mwd_metrics.f90 lines 118-141
    
    Parameters
    ----------
    x : float array
    y : float array
    
    Returns
    -------
    res : float
    
    Notes
    -----
    
    KGE computation function
    
    Given two single precision array(x, y) of dim(1) and size(n),
    it returns the result of KGE computation
    KGE = 1 - sqrt((r - 1) ** 2 + (b - 1) ** 2 + (a - 1) ** 2)
    
    See Also
    --------
    kge_components
    """
    res = _libfcore.f90wrap_mwd_metrics__kge(x=x, y=y)
    return res

def mae(x, y):
    """
    res = mae(x, y)
    
    
    Defined at ../smash/fcore/signal_analysis/mwd_metrics.f90 lines 143-163
    
    Parameters
    ----------
    x : float array
    y : float array
    
    Returns
    -------
    res : float
    
    Notes
    -----
    
    Mean Absolute Error(MAE) computation function
    
    Given two single precision arrays(x, y) of size n,
    it returns the result of MAE computation
    MAE = sum(abs(x - y)) / n
    """
    res = _libfcore.f90wrap_mwd_metrics__mae(x=x, y=y)
    return res

def mape(x, y):
    """
    res = mape(x, y)
    
    
    Defined at ../smash/fcore/signal_analysis/mwd_metrics.f90 lines 165-185
    
    Parameters
    ----------
    x : float array
    y : float array
    
    Returns
    -------
    res : float
    
    Notes
    -----
    
    Mean Absolute Percentage Error(MAPE) computation function
    
    Given two single precision arrays(x, y) of size n,
    it returns the result of MAPE computation
    MAPE = sum(abs((x - y) / x)) / n
    """
    res = _libfcore.f90wrap_mwd_metrics__mape(x=x, y=y)
    return res

def se(x, y):
    """
    res = se(x, y)
    
    
    Defined at ../smash/fcore/signal_analysis/mwd_metrics.f90 lines 187-204
    
    Parameters
    ----------
    x : float array
    y : float array
    
    Returns
    -------
    res : float
    
    Notes
    -----
    
    Squared Error(SE) computation function
    
    Given two single precision array(x, y) of dim(1) and size(n),
    it returns the result of SE computation
    SE = sum((x - y) ** 2)
    """
    res = _libfcore.f90wrap_mwd_metrics__se(x=x, y=y)
    return res

def mse(x, y):
    """
    res = mse(x, y)
    
    
    Defined at ../smash/fcore/signal_analysis/mwd_metrics.f90 lines 206-228
    
    Parameters
    ----------
    x : float array
    y : float array
    
    Returns
    -------
    res : float
    
    Notes
    -----
    
    Mean Squared Error(MSE) computation function
    
    Given two single precision arrays(x, y) of size n,
    it returns the result of MSE computation
    MSE = SE / n
    
    See Also
    --------
    se
    """
    res = _libfcore.f90wrap_mwd_metrics__mse(x=x, y=y)
    return res

def rmse(x, y):
    """
    res = rmse(x, y)
    
    
    Defined at ../smash/fcore/signal_analysis/mwd_metrics.f90 lines 230-246
    
    Parameters
    ----------
    x : float array
    y : float array
    
    Returns
    -------
    res : float
    
    Notes
    -----
    
    Root Mean Squared Error(RMSE) computation function
    
    Given two single precision array(x, y) of dim(1) and size(n),
    it returns the result of SE computation
    RMSE = sqrt(MSE)
    
    See Also
    --------
    mse
    """
    res = _libfcore.f90wrap_mwd_metrics__rmse(x=x, y=y)
    return res

def lgrm(x, y):
    """
    res = lgrm(x, y)
    
    
    Defined at ../smash/fcore/signal_analysis/mwd_metrics.f90 lines 248-265
    
    Parameters
    ----------
    x : float array
    y : float array
    
    Returns
    -------
    res : float
    
    Notes
    -----
    
    Logarithmic(LGRM) computation function
    
    Given two single precision array(x, y) of dim(1) and size(n),
    it returns the result of LGRM computation
    LGRM = sum(x * log(y/x) ** 2)
    """
    res = _libfcore.f90wrap_mwd_metrics__lgrm(x=x, y=y)
    return res


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_metrics".')

for func in _dt_array_initialisers:
    func()

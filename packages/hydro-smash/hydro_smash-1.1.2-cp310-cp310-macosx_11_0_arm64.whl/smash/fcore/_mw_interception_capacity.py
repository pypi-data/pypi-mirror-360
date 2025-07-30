"""
Module mw_interception_capacity


Defined at ../smash/fcore/routine/mw_interception_capacity.f90 lines 7-90

(MW) Module Wrapped.

Subroutine
----------

- adjust_interception_capacity
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

def adjust_interception_capacity(self, mesh, input_data, day_index, nday, ci):
    """
    adjust_interception_capacity(self, mesh, input_data, day_index, nday, ci)
    
    
    Defined at ../smash/fcore/routine/mw_interception_capacity.f90 lines 18-90
    
    Parameters
    ----------
    setup : Setupdt
    mesh : Meshdt
    input_data : Input_Datadt
    day_index : int array
    nday : int
    ci : float array
    
    Daily aggregation of precipitation and evapotranspiration
    =========================================================================================================== \
        %
    =========================================================================================================== \
        %
    Calculate interception storage
    =========================================================================================================== \
        %
    """
    _libfcore.f90wrap_mw_interception_capacity__adjust_interception_capacity(setup=self._handle, \
        mesh=mesh._handle, input_data=input_data._handle, day_index=day_index, \
        nday=nday, ci=ci)


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mw_interception_capacity".')

for func in _dt_array_initialisers:
    func()

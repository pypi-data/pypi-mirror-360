"""
Module mw_atmos_statistic


Defined at ../smash/fcore/routine/mw_atmos_statistic.f90 lines 9-118

(MW) Module Wrapped.

Subroutine
----------

- get_mean_gauge_atmos_data
- compute_mean_atmos
- compute_prcp_partitioning
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

def get_mean_gauge_atmos_data(self, mask_gauge, mask_atmos, mat_atmos, \
    mean_gauge_atmos):
    """
    get_mean_gauge_atmos_data(self, mask_gauge, mask_atmos, mat_atmos, \
        mean_gauge_atmos)
    
    
    Defined at ../smash/fcore/routine/mw_atmos_statistic.f90 lines 19-40
    
    Parameters
    ----------
    mesh : Meshdt
    mask_gauge : bool array
    mask_atmos : bool array
    mat_atmos : float array
    mean_gauge_atmos : float
    
    """
    _libfcore.f90wrap_mw_atmos_statistic__get_mean_gauge_atmos_data(mesh=self._handle, \
        mask_gauge=mask_gauge, mask_atmos=mask_atmos, mat_atmos=mat_atmos, \
        mean_gauge_atmos=mean_gauge_atmos)

def compute_mean_atmos(self, mesh, input_data):
    """
    compute_mean_atmos(self, mesh, input_data)
    
    
    Defined at ../smash/fcore/routine/mw_atmos_statistic.f90 lines 44-90
    
    Parameters
    ----------
    setup : Setupdt
    mesh : Meshdt
    input_data : Input_Datadt
    
    Only allocate snow and temp variables if a snow module has been choosen
    """
    _libfcore.f90wrap_mw_atmos_statistic__compute_mean_atmos(setup=self._handle, \
        mesh=mesh._handle, input_data=input_data._handle)

def compute_prcp_partitioning(self, mesh, input_data):
    """
    compute_prcp_partitioning(self, mesh, input_data)
    
    
    Defined at ../smash/fcore/routine/mw_atmos_statistic.f90 lines 92-118
    
    Parameters
    ----------
    setup : Setupdt
    mesh : Meshdt
    input_data : Input_Datadt
    
    """
    _libfcore.f90wrap_mw_atmos_statistic__compute_prcp_partitioning(setup=self._handle, \
        mesh=mesh._handle, input_data=input_data._handle)


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mw_atmos_statistic".')

for func in _dt_array_initialisers:
    func()

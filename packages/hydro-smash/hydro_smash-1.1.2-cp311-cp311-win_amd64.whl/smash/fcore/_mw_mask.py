"""
Module mw_mask


Defined at ../smash/fcore/routine/mw_mask.f90 lines 7-26

(MW) Module Wrapped.

Subroutine
----------

- mask_upstream_cells
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

def mask_upstream_cells(self, row, col, mask):
    """
    mask_upstream_cells(self, row, col, mask)
    
    
    Defined at ../smash/fcore/routine/mw_mask.f90 lines 11-26
    
    Parameters
    ----------
    mesh : Meshdt
    row : int
    col : int
    mask : bool array
    
    """
    _libfcore.f90wrap_mw_mask__mask_upstream_cells(mesh=self._handle, row=row, \
        col=col, mask=mask)


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module "mw_mask".')

for func in _dt_array_initialisers:
    func()

"""
Module mwd_options


Defined at ../smash/fcore/derived_type/mwd_options.f90 lines 22-49

(MWD) Module Wrapped and Differentiated.

Type
----

- OptionsDT
Container for all user options(optimize, cost, common)

======================== =======================================
`Variables`              Description
======================== =======================================
``optimize``             Optimize_OptionsDT
``cost``                 Cost_OptionsDT
``comm``                 Common_OptionsDT
======================== =======================================

Subroutine
----------

- OptionsDT_initialise
- OptionsDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy
from smash.fcore._mwd_cost_options import Cost_OptionsDT
from smash.fcore._mwd_optimize_options import Optimize_OptionsDT
from smash.fcore._mwd_common_options import Common_OptionsDT

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.OptionsDT")
class OptionsDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return optionsdt_copy(self)
    """
    Type(name=optionsdt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_options.f90 lines 29-32
    
    """
    def __init__(self, setup, mesh, njoc, njrc, handle=None):
        """
        self = Optionsdt(setup, mesh, njoc, njrc)
        
        
        Defined at ../smash/fcore/derived_type/mwd_options.f90 lines 35-43
        
        Parameters
        ----------
        setup : Setupdt
        mesh : Meshdt
        njoc : int
        njrc : int
        
        Returns
        -------
        this : Optionsdt
        
        only: SetupDT
        only: MeshDT
        only: Cost_OptionsDT, Cost_OptionsDT_initialise
        only: Optimize_OptionsDT, Optimize_OptionsDT_initialise
        only: Common_OptionsDT, Common_OptionsDT_initialise
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = \
            _libfcore.f90wrap_mwd_options__optionsdt_initialise(setup=setup._handle, \
            mesh=mesh._handle, njoc=njoc, njrc=njrc)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Optionsdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_options.f90 lines 29-32
        
        Parameters
        ----------
        this : Optionsdt
            Object to be destructed
        
        
        Automatically generated destructor for optionsdt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_options__optionsdt_finalise(this=self._handle)
        except:
            pass
    
    @property
    def optimize(self):
        """
        Element optimize ftype=type(optimize_optionsdt) pytype=Optimize_Optionsdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_options.f90 line 30
        
        """
        optimize_handle = _libfcore.f90wrap_optionsdt__get__optimize(self._handle)
        if tuple(optimize_handle) in self._objs:
            optimize = self._objs[tuple(optimize_handle)]
        else:
            optimize = Optimize_OptionsDT.from_handle(optimize_handle)
            self._objs[tuple(optimize_handle)] = optimize
        return optimize
    
    @optimize.setter
    def optimize(self, optimize):
        optimize = optimize._handle
        _libfcore.f90wrap_optionsdt__set__optimize(self._handle, optimize)
    
    @property
    def cost(self):
        """
        Element cost ftype=type(cost_optionsdt) pytype=Cost_Optionsdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_options.f90 line 31
        
        """
        cost_handle = _libfcore.f90wrap_optionsdt__get__cost(self._handle)
        if tuple(cost_handle) in self._objs:
            cost = self._objs[tuple(cost_handle)]
        else:
            cost = Cost_OptionsDT.from_handle(cost_handle)
            self._objs[tuple(cost_handle)] = cost
        return cost
    
    @cost.setter
    def cost(self, cost):
        cost = cost._handle
        _libfcore.f90wrap_optionsdt__set__cost(self._handle, cost)
    
    @property
    def comm(self):
        """
        Element comm ftype=type(common_optionsdt) pytype=Common_Optionsdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_options.f90 line 32
        
        """
        comm_handle = _libfcore.f90wrap_optionsdt__get__comm(self._handle)
        if tuple(comm_handle) in self._objs:
            comm = self._objs[tuple(comm_handle)]
        else:
            comm = Common_OptionsDT.from_handle(comm_handle)
            self._objs[tuple(comm_handle)] = comm
        return comm
    
    @comm.setter
    def comm(self, comm):
        comm = comm._handle
        _libfcore.f90wrap_optionsdt__set__comm(self._handle, comm)
    
    
    def __repr__(self):
        ret = [self.__class__.__name__]
        for attr in dir(self):
            if attr.startswith("_"):
                continue
            try:
                value = getattr(self, attr)
            except Exception:
                continue
            if callable(value):
                continue
            elif isinstance(value, f90wrap.runtime.FortranDerivedTypeArray):
                n = len(value)
                nrepr = 4
                if n == 0:
                    continue
                else:
                    repr_value = [value[0].__class__.__name__] * min(n, nrepr)
                if n > nrepr:
                    repr_value.insert(2, "...")
                repr_value = repr(repr_value)
            else:
                repr_value = repr(value)
            ret.append(f"    {attr}: {repr_value}")
        return "\n".join(ret)
    
    
    _dt_array_initialisers = []
    

def optionsdt_copy(self):
    """
    this_copy = optionsdt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_options.f90 lines 45-49
    
    Parameters
    ----------
    this : Optionsdt
    
    Returns
    -------
    this_copy : Optionsdt
    
    """
    this_copy = _libfcore.f90wrap_mwd_options__optionsdt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.OptionsDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_options".')

for func in _dt_array_initialisers:
    func()

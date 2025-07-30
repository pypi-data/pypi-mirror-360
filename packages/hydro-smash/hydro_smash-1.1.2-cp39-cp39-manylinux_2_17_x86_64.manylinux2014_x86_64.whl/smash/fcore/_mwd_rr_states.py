"""
Module mwd_rr_states


Defined at ../smash/fcore/derived_type/mwd_rr_states.f90 lines 21-46

(MWD) Module Wrapped and Differentiated.

Type
----

- RR_StatesDT
Matrices containting spatialized states of hydrological operators.
(reservoir level ...) The matrices are updated at each time step.

========================== =====================================
`Variables`                Description
========================== =====================================
``keys``                   Rainfall-runoff states keys
``values``                 Rainfall-runoff states values

----------

- RR_StatesDT_initialise
- RR_StatesDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore._f90wrap_decorator import f90wrap_getter_char_array, f90wrap_setter_char_array
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.RR_StatesDT")
class RR_StatesDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return rr_statesdt_copy(self)
    """
    Type(name=rr_statesdt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_rr_states.f90 lines 26-28
    
    """
    def __init__(self, setup, mesh, handle=None):
        """
        self = Rr_Statesdt(setup, mesh)
        
        
        Defined at ../smash/fcore/derived_type/mwd_rr_states.f90 lines 31-40
        
        Parameters
        ----------
        setup : Setupdt
        mesh : Meshdt
        
        Returns
        -------
        this : Rr_Statesdt
        
        Default states value will be handled in Python
        only: sp, lchar
        only: SetupDT
        only: MeshDT
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = \
            _libfcore.f90wrap_mwd_rr_states__rr_statesdt_initialise(setup=setup._handle, \
            mesh=mesh._handle)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Rr_Statesdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_rr_states.f90 lines 26-28
        
        Parameters
        ----------
        this : Rr_Statesdt
            Object to be destructed
        
        
        Automatically generated destructor for rr_statesdt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_rr_states__rr_statesdt_finalise(this=self._handle)
        except:
            pass
    
    @property
    @f90wrap_getter_char_array
    def keys(self):
        """
        Element keys ftype=character(lchar) pytype=str
        
        
        Defined at ../smash/fcore/derived_type/mwd_rr_states.f90 line 27
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_rr_statesdt__array__keys(self._handle)
        if array_handle in self._arrays:
            keys = self._arrays[array_handle]
        else:
            keys = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_rr_statesdt__array__keys)
            self._arrays[array_handle] = keys
        return keys
    
    @keys.setter
    @f90wrap_setter_char_array
    def keys(self, keys):
        self.keys[...] = keys
    
    @property
    def values(self):
        """
        Element values ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_rr_states.f90 line 28
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_rr_statesdt__array__values(self._handle)
        if array_handle in self._arrays:
            values = self._arrays[array_handle]
        else:
            values = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_rr_statesdt__array__values)
            self._arrays[array_handle] = values
        return values
    
    @values.setter
    def values(self, values):
        self.values[...] = values
    
    
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
    

def rr_statesdt_copy(self):
    """
    this_copy = rr_statesdt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_rr_states.f90 lines 42-46
    
    Parameters
    ----------
    this : Rr_Statesdt
    
    Returns
    -------
    this_copy : Rr_Statesdt
    
    """
    this_copy = _libfcore.f90wrap_mwd_rr_states__rr_statesdt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.RR_StatesDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_rr_states".')

for func in _dt_array_initialisers:
    func()

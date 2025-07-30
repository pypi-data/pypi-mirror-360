"""
Module mwd_response


Defined at ../smash/fcore/derived_type/mwd_response.f90 lines 20-41

(MWD) Module Wrapped and Differentiated.

Type
----

- ResponseDT
Response simulated by the hydrological model.

======================== =======================================
`Variables`              Description
======================== =======================================
``q``                    Simulated discharge at gauges              [m3/s]
======================== =======================================

Subroutine
----------

- ResponseDT_initialise
- ResponseDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.ResponseDT")
class ResponseDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return responsedt_copy(self)
    """
    Type(name=responsedt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_response.f90 lines 25-26
    
    """
    def __init__(self, setup, mesh, handle=None):
        """
        self = Responsedt(setup, mesh)
        
        
        Defined at ../smash/fcore/derived_type/mwd_response.f90 lines 29-35
        
        Parameters
        ----------
        setup : Setupdt
        mesh : Meshdt
        
        Returns
        -------
        this : Responsedt
        
        only: sp
        only: SetupDT
        only: MeshDT
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = \
            _libfcore.f90wrap_mwd_response__responsedt_initialise(setup=setup._handle, \
            mesh=mesh._handle)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Responsedt
        
        
        Defined at ../smash/fcore/derived_type/mwd_response.f90 lines 25-26
        
        Parameters
        ----------
        this : Responsedt
            Object to be destructed
        
        
        Automatically generated destructor for responsedt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_response__responsedt_finalise(this=self._handle)
        except:
            pass
    
    @property
    def q(self):
        """
        Element q ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_response.f90 line 26
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_responsedt__array__q(self._handle)
        if array_handle in self._arrays:
            q = self._arrays[array_handle]
        else:
            q = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_responsedt__array__q)
            self._arrays[array_handle] = q
        return q
    
    @q.setter
    def q(self, q):
        self.q[...] = q
    
    
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
    

def responsedt_copy(self):
    """
    this_copy = responsedt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_response.f90 lines 37-41
    
    Parameters
    ----------
    this : Responsedt
    
    Returns
    -------
    this_copy : Responsedt
    
    """
    this_copy = _libfcore.f90wrap_mwd_response__responsedt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.ResponseDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_response".')

for func in _dt_array_initialisers:
    func()

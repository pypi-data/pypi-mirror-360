"""
Module mwd_u_response_data


Defined at ../smash/fcore/derived_type/mwd_u_response_data.f90 lines 20-41

(MWD) Module Wrapped and Differentiated.

Type
----

- U_Response_DataDT
User-provided observation uncertainties for the hydrological model response \
    variables

======================== =======================================
`Variables`              Description
======================== =======================================
``q_stdev`` Discharge uncertainty at gauges(standard deviation of independent \
    error) [m3/s]
======================== =======================================

Subroutine
----------

- U_Response_DataDT_initialise
- U_Response_DataDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.U_Response_DataDT")
class U_Response_DataDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return u_response_datadt_copy(self)
    """
    Type(name=u_response_datadt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_u_response_data.f90 lines 25-26
    
    """
    def __init__(self, setup, mesh, handle=None):
        """
        self = U_Response_Datadt(setup, mesh)
        
        
        Defined at ../smash/fcore/derived_type/mwd_u_response_data.f90 lines 29-35
        
        Parameters
        ----------
        setup : Setupdt
        mesh : Meshdt
        
        Returns
        -------
        this : U_Response_Datadt
        
        only: sp
        only: SetupDT
        only: MeshDT
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = \
            _libfcore.f90wrap_mwd_u_response_data__u_response_datadt_initialise(setup=setup._handle, \
            mesh=mesh._handle)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class U_Response_Datadt
        
        
        Defined at ../smash/fcore/derived_type/mwd_u_response_data.f90 lines 25-26
        
        Parameters
        ----------
        this : U_Response_Datadt
            Object to be destructed
        
        
        Automatically generated destructor for u_response_datadt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_u_response_data__u_response_datadt_finalise(this=self._handle)
        except:
            pass
    
    @property
    def q_stdev(self):
        """
        Element q_stdev ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_u_response_data.f90 line 26
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_u_response_datadt__array__q_stdev(self._handle)
        if array_handle in self._arrays:
            q_stdev = self._arrays[array_handle]
        else:
            q_stdev = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_u_response_datadt__array__q_stdev)
            self._arrays[array_handle] = q_stdev
        return q_stdev
    
    @q_stdev.setter
    def q_stdev(self, q_stdev):
        self.q_stdev[...] = q_stdev
    
    
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
    

def u_response_datadt_copy(self):
    """
    this_copy = u_response_datadt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_u_response_data.f90 lines 37-41
    
    Parameters
    ----------
    this : U_Response_Datadt
    
    Returns
    -------
    this_copy : U_Response_Datadt
    
    """
    this_copy = \
        _libfcore.f90wrap_mwd_u_response_data__u_response_datadt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.U_Response_DataDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_u_response_data".')

for func in _dt_array_initialisers:
    func()

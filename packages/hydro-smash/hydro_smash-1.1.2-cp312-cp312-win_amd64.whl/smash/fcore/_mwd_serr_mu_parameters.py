"""
Module mwd_serr_mu_parameters


Defined at ../smash/fcore/derived_type/mwd_serr_mu_parameters.f90 lines 22-46

(MWD) Module Wrapped and Differentiated.

Type
----

- SErr_Mu_ParametersDT
Vectors containting hyper parameters of the temporalisation function for mu, the \
    mean of structural errors
(mg0, mg1, ...)

======================== =============================================
`Variables`              Description
======================== =============================================
``keys``                 Structural errors mu hyper parameters keys
``values``               Structural errors mu hyper parameters values
======================== =============================================

Subroutine
----------

- SErr_Mu_ParametersDT_initialise
- SErr_Mu_ParametersDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore._f90wrap_decorator import f90wrap_getter_char_array, f90wrap_setter_char_array
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.SErr_Mu_ParametersDT")
class SErr_Mu_ParametersDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return serr_mu_parametersdt_copy(self)
    """
    Type(name=serr_mu_parametersdt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_serr_mu_parameters.f90 lines 27-29
    
    """
    def __init__(self, setup, mesh, handle=None):
        """
        self = Serr_Mu_Parametersdt(setup, mesh)
        
        
        Defined at ../smash/fcore/derived_type/mwd_serr_mu_parameters.f90 lines 32-40
        
        Parameters
        ----------
        setup : Setupdt
        mesh : Meshdt
        
        Returns
        -------
        this : Serr_Mu_Parametersdt
        
        only: sp, lchar
        only: SetupDT
        only: MeshDT
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = \
            _libfcore.f90wrap_mwd_serr_mu_parameters__serr_mu_parametersdt_initialise(setup=setup._handle, \
            mesh=mesh._handle)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Serr_Mu_Parametersdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_serr_mu_parameters.f90 lines 27-29
        
        Parameters
        ----------
        this : Serr_Mu_Parametersdt
            Object to be destructed
        
        
        Automatically generated destructor for serr_mu_parametersdt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_serr_mu_parameters__serr_mu_parametersdt_finalise(this=self._handle)
        except:
            pass
    
    @property
    @f90wrap_getter_char_array
    def keys(self):
        """
        Element keys ftype=character(lchar) pytype=str
        
        
        Defined at ../smash/fcore/derived_type/mwd_serr_mu_parameters.f90 line 28
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_serr_mu_parametersdt__array__keys(self._handle)
        if array_handle in self._arrays:
            keys = self._arrays[array_handle]
        else:
            keys = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_serr_mu_parametersdt__array__keys)
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
        
        
        Defined at ../smash/fcore/derived_type/mwd_serr_mu_parameters.f90 line 29
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_serr_mu_parametersdt__array__values(self._handle)
        if array_handle in self._arrays:
            values = self._arrays[array_handle]
        else:
            values = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_serr_mu_parametersdt__array__values)
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
    

def serr_mu_parametersdt_copy(self):
    """
    this_copy = serr_mu_parametersdt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_serr_mu_parameters.f90 lines 42-46
    
    Parameters
    ----------
    this : Serr_Mu_Parametersdt
    
    Returns
    -------
    this_copy : Serr_Mu_Parametersdt
    
    """
    this_copy = \
        _libfcore.f90wrap_mwd_serr_mu_parameters__serr_mu_parametersdt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.SErr_Mu_ParametersDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_serr_mu_parameters".')

for func in _dt_array_initialisers:
    func()

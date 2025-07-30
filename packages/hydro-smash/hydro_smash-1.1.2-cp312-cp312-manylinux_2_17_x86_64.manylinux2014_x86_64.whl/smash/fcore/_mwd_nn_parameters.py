"""
Module mwd_nn_parameters


Defined at ../smash/fcore/derived_type/mwd_nn_parameters.f90 lines 25-62

(MWD) Module Wrapped and Differentiated.

Type
----

- NN_ParametersDT
Contain weights and biases of the neural network

======================== \
    ===========================================================
`Variables`              Description
======================== \
    ===========================================================
``weight_1`` Transposed weight at the first layer of the neural network
``bias_1``               Bias at the first layer of the neural network
``weight_2`` Transposed weight at the second layer of the neural network
``bias_2``               Bias at the second layer of the neural network
``weight_3`` Transposed weight at the third layer of the neural network
``bias_3``               Bias at the third layer of the neural network
======================== \
    ===========================================================

Subroutine
----------

- NN_ParametersDT_initialise
- NN_ParametersDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.NN_ParametersDT")
class NN_ParametersDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return nn_parametersdt_copy(self)
    """
    Type(name=nn_parametersdt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_nn_parameters.f90 lines 29-35
    
    """
    def __init__(self, setup, handle=None):
        """
        self = Nn_Parametersdt(setup)
        
        
        Defined at ../smash/fcore/derived_type/mwd_nn_parameters.f90 lines 38-56
        
        Parameters
        ----------
        setup : Setupdt
            First layer
        
        
        Returns
        -------
        this : Nn_Parametersdt
        
        Second layer
        Third layer
        only: sp
        only: SetupDT
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = \
            _libfcore.f90wrap_mwd_nn_parameters__nn_parametersdt_initialise(setup=setup._handle)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Nn_Parametersdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_nn_parameters.f90 lines 29-35
        
        Parameters
        ----------
        this : Nn_Parametersdt
            Object to be destructed
        
        
        Automatically generated destructor for nn_parametersdt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_nn_parameters__nn_parametersdt_finalise(this=self._handle)
        except:
            pass
    
    @property
    def weight_1(self):
        """
        Element weight_1 ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_nn_parameters.f90 line 30
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_nn_parametersdt__array__weight_1(self._handle)
        if array_handle in self._arrays:
            weight_1 = self._arrays[array_handle]
        else:
            weight_1 = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_nn_parametersdt__array__weight_1)
            self._arrays[array_handle] = weight_1
        return weight_1
    
    @weight_1.setter
    def weight_1(self, weight_1):
        self.weight_1[...] = weight_1
    
    @property
    def bias_1(self):
        """
        Element bias_1 ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_nn_parameters.f90 line 31
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_nn_parametersdt__array__bias_1(self._handle)
        if array_handle in self._arrays:
            bias_1 = self._arrays[array_handle]
        else:
            bias_1 = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_nn_parametersdt__array__bias_1)
            self._arrays[array_handle] = bias_1
        return bias_1
    
    @bias_1.setter
    def bias_1(self, bias_1):
        self.bias_1[...] = bias_1
    
    @property
    def weight_2(self):
        """
        Element weight_2 ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_nn_parameters.f90 line 32
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_nn_parametersdt__array__weight_2(self._handle)
        if array_handle in self._arrays:
            weight_2 = self._arrays[array_handle]
        else:
            weight_2 = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_nn_parametersdt__array__weight_2)
            self._arrays[array_handle] = weight_2
        return weight_2
    
    @weight_2.setter
    def weight_2(self, weight_2):
        self.weight_2[...] = weight_2
    
    @property
    def bias_2(self):
        """
        Element bias_2 ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_nn_parameters.f90 line 33
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_nn_parametersdt__array__bias_2(self._handle)
        if array_handle in self._arrays:
            bias_2 = self._arrays[array_handle]
        else:
            bias_2 = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_nn_parametersdt__array__bias_2)
            self._arrays[array_handle] = bias_2
        return bias_2
    
    @bias_2.setter
    def bias_2(self, bias_2):
        self.bias_2[...] = bias_2
    
    @property
    def weight_3(self):
        """
        Element weight_3 ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_nn_parameters.f90 line 34
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_nn_parametersdt__array__weight_3(self._handle)
        if array_handle in self._arrays:
            weight_3 = self._arrays[array_handle]
        else:
            weight_3 = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_nn_parametersdt__array__weight_3)
            self._arrays[array_handle] = weight_3
        return weight_3
    
    @weight_3.setter
    def weight_3(self, weight_3):
        self.weight_3[...] = weight_3
    
    @property
    def bias_3(self):
        """
        Element bias_3 ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_nn_parameters.f90 line 35
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_nn_parametersdt__array__bias_3(self._handle)
        if array_handle in self._arrays:
            bias_3 = self._arrays[array_handle]
        else:
            bias_3 = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_nn_parametersdt__array__bias_3)
            self._arrays[array_handle] = bias_3
        return bias_3
    
    @bias_3.setter
    def bias_3(self, bias_3):
        self.bias_3[...] = bias_3
    
    
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
    

def nn_parametersdt_copy(self):
    """
    this_copy = nn_parametersdt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_nn_parameters.f90 lines 58-62
    
    Parameters
    ----------
    this : Nn_Parametersdt
    
    Returns
    -------
    this_copy : Nn_Parametersdt
    
    """
    this_copy = \
        _libfcore.f90wrap_mwd_nn_parameters__nn_parametersdt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.NN_ParametersDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_nn_parameters".')

for func in _dt_array_initialisers:
    func()

"""
Module mwd_optimize_options


Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 lines 38-102

(MWD) Module Wrapped and Differentiated.

Type
----

- Optimize_OptionsDT
Optimization options passed by user to define the 'parameters-to-control' \
    mapping,
parameters to optimize and optimizer options(factr, pgtol, bounds)

================================== =======================================
`Variables`                        Description
================================== =======================================
``mapping``                       Control mapping name
``optimizer``                     Optimizer name
``control_tfm``                   Type of transformation applied to control
``rr_parameters``                 RR parameters to optimize
``l_rr_parameters``               RR parameters lower bound
``u_rr_parameters``               RR parameters upper bound
``nn_parameters``                 NN parameters to optimize
``rr_parameters_descriptor``      RR parameters descriptor to use
``rr_initial_states``             RR initial states to optimize
``l_rr_initial_states``           RR initial states lower bound
``u_rr_initial_states``           RR initial states upper bound
``rr_initial_states_descriptor``  RR initial states descriptor use
``serr_mu_parameters``            SErr mu parameters to optimize
``l_serr_mu_parameters``          SErr mu parameters lower bound
``u_serr_mu_parameters``          SErr mu parameters upper bound
``serr_sigma_parameters``         SErr sigma parameters to optimize
``l_serr_sigma_parameters``       SErr sigma parameters lower bound
``u_serr_sigma_parameters``       SErr sigma parameters upper bound
================================== =======================================

Subroutine
----------

- Optimize_OptionsDT_initialise
- Optimize_OptionsDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore._f90wrap_decorator import f90wrap_getter_char, f90wrap_setter_char
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.Optimize_OptionsDT")
class Optimize_OptionsDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return optimize_optionsdt_copy(self)
    """
    Type(name=optimize_optionsdt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 lines 42-60
    
    """
    def __init__(self, setup, handle=None):
        """
        self = Optimize_Optionsdt(setup)
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 lines 63-96
        
        Parameters
        ----------
        setup : Setupdt
        
        Returns
        -------
        this : Optimize_Optionsdt
        
        only: sp, lchar
        only: SetupDT
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = \
            _libfcore.f90wrap_mwd_optimize_options__optimize_optionsdt_initialise(setup=setup._handle)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Optimize_Optionsdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 lines 42-60
        
        Parameters
        ----------
        this : Optimize_Optionsdt
            Object to be destructed
        
        
        Automatically generated destructor for optimize_optionsdt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_optimize_options__optimize_optionsdt_finalise(this=self._handle)
        except:
            pass
    
    @property
    @f90wrap_getter_char
    def mapping(self):
        """
        Element mapping ftype=character(lchar) pytype=str
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 43
        
        """
        return _libfcore.f90wrap_optimize_optionsdt__get__mapping(self._handle)
    
    @mapping.setter
    @f90wrap_setter_char
    def mapping(self, mapping):
        _libfcore.f90wrap_optimize_optionsdt__set__mapping(self._handle, mapping)
    
    @property
    @f90wrap_getter_char
    def optimizer(self):
        """
        Element optimizer ftype=character(lchar) pytype=str
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 44
        
        """
        return _libfcore.f90wrap_optimize_optionsdt__get__optimizer(self._handle)
    
    @optimizer.setter
    @f90wrap_setter_char
    def optimizer(self, optimizer):
        _libfcore.f90wrap_optimize_optionsdt__set__optimizer(self._handle, optimizer)
    
    @property
    @f90wrap_getter_char
    def control_tfm(self):
        """
        Element control_tfm ftype=character(lchar) pytype=str
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 45
        
        """
        return _libfcore.f90wrap_optimize_optionsdt__get__control_tfm(self._handle)
    
    @control_tfm.setter
    @f90wrap_setter_char
    def control_tfm(self, control_tfm):
        _libfcore.f90wrap_optimize_optionsdt__set__control_tfm(self._handle, \
            control_tfm)
    
    @property
    def rr_parameters(self):
        """
        Element rr_parameters ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 46
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__rr_parameters(self._handle)
        if array_handle in self._arrays:
            rr_parameters = self._arrays[array_handle]
        else:
            rr_parameters = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__rr_parameters)
            self._arrays[array_handle] = rr_parameters
        return rr_parameters
    
    @rr_parameters.setter
    def rr_parameters(self, rr_parameters):
        self.rr_parameters[...] = rr_parameters
    
    @property
    def l_rr_parameters(self):
        """
        Element l_rr_parameters ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 47
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__l_rr_parameters(self._handle)
        if array_handle in self._arrays:
            l_rr_parameters = self._arrays[array_handle]
        else:
            l_rr_parameters = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__l_rr_parameters)
            self._arrays[array_handle] = l_rr_parameters
        return l_rr_parameters
    
    @l_rr_parameters.setter
    def l_rr_parameters(self, l_rr_parameters):
        self.l_rr_parameters[...] = l_rr_parameters
    
    @property
    def u_rr_parameters(self):
        """
        Element u_rr_parameters ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 48
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__u_rr_parameters(self._handle)
        if array_handle in self._arrays:
            u_rr_parameters = self._arrays[array_handle]
        else:
            u_rr_parameters = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__u_rr_parameters)
            self._arrays[array_handle] = u_rr_parameters
        return u_rr_parameters
    
    @u_rr_parameters.setter
    def u_rr_parameters(self, u_rr_parameters):
        self.u_rr_parameters[...] = u_rr_parameters
    
    @property
    def rr_parameters_descriptor(self):
        """
        Element rr_parameters_descriptor ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 49
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__rr_parameters_descriptor(self._handle)
        if array_handle in self._arrays:
            rr_parameters_descriptor = self._arrays[array_handle]
        else:
            rr_parameters_descriptor = \
                f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__rr_parameters_descriptor)
            self._arrays[array_handle] = rr_parameters_descriptor
        return rr_parameters_descriptor
    
    @rr_parameters_descriptor.setter
    def rr_parameters_descriptor(self, rr_parameters_descriptor):
        self.rr_parameters_descriptor[...] = rr_parameters_descriptor
    
    @property
    def nn_parameters(self):
        """
        Element nn_parameters ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 50
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__nn_parameters(self._handle)
        if array_handle in self._arrays:
            nn_parameters = self._arrays[array_handle]
        else:
            nn_parameters = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__nn_parameters)
            self._arrays[array_handle] = nn_parameters
        return nn_parameters
    
    @nn_parameters.setter
    def nn_parameters(self, nn_parameters):
        self.nn_parameters[...] = nn_parameters
    
    @property
    def rr_initial_states(self):
        """
        Element rr_initial_states ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 51
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__rr_initial_states(self._handle)
        if array_handle in self._arrays:
            rr_initial_states = self._arrays[array_handle]
        else:
            rr_initial_states = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__rr_initial_states)
            self._arrays[array_handle] = rr_initial_states
        return rr_initial_states
    
    @rr_initial_states.setter
    def rr_initial_states(self, rr_initial_states):
        self.rr_initial_states[...] = rr_initial_states
    
    @property
    def l_rr_initial_states(self):
        """
        Element l_rr_initial_states ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 52
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__l_rr_initial_states(self._handle)
        if array_handle in self._arrays:
            l_rr_initial_states = self._arrays[array_handle]
        else:
            l_rr_initial_states = \
                f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__l_rr_initial_states)
            self._arrays[array_handle] = l_rr_initial_states
        return l_rr_initial_states
    
    @l_rr_initial_states.setter
    def l_rr_initial_states(self, l_rr_initial_states):
        self.l_rr_initial_states[...] = l_rr_initial_states
    
    @property
    def u_rr_initial_states(self):
        """
        Element u_rr_initial_states ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 53
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__u_rr_initial_states(self._handle)
        if array_handle in self._arrays:
            u_rr_initial_states = self._arrays[array_handle]
        else:
            u_rr_initial_states = \
                f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__u_rr_initial_states)
            self._arrays[array_handle] = u_rr_initial_states
        return u_rr_initial_states
    
    @u_rr_initial_states.setter
    def u_rr_initial_states(self, u_rr_initial_states):
        self.u_rr_initial_states[...] = u_rr_initial_states
    
    @property
    def rr_initial_states_descriptor(self):
        """
        Element rr_initial_states_descriptor ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 54
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__rr_initial_states_descriptor(self._handle)
        if array_handle in self._arrays:
            rr_initial_states_descriptor = self._arrays[array_handle]
        else:
            rr_initial_states_descriptor = \
                f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__rr_initial_states_descriptor)
            self._arrays[array_handle] = rr_initial_states_descriptor
        return rr_initial_states_descriptor
    
    @rr_initial_states_descriptor.setter
    def rr_initial_states_descriptor(self, rr_initial_states_descriptor):
        self.rr_initial_states_descriptor[...] = rr_initial_states_descriptor
    
    @property
    def serr_mu_parameters(self):
        """
        Element serr_mu_parameters ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 55
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__serr_mu_parameters(self._handle)
        if array_handle in self._arrays:
            serr_mu_parameters = self._arrays[array_handle]
        else:
            serr_mu_parameters = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__serr_mu_parameters)
            self._arrays[array_handle] = serr_mu_parameters
        return serr_mu_parameters
    
    @serr_mu_parameters.setter
    def serr_mu_parameters(self, serr_mu_parameters):
        self.serr_mu_parameters[...] = serr_mu_parameters
    
    @property
    def l_serr_mu_parameters(self):
        """
        Element l_serr_mu_parameters ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 56
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__l_serr_mu_parameters(self._handle)
        if array_handle in self._arrays:
            l_serr_mu_parameters = self._arrays[array_handle]
        else:
            l_serr_mu_parameters = \
                f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__l_serr_mu_parameters)
            self._arrays[array_handle] = l_serr_mu_parameters
        return l_serr_mu_parameters
    
    @l_serr_mu_parameters.setter
    def l_serr_mu_parameters(self, l_serr_mu_parameters):
        self.l_serr_mu_parameters[...] = l_serr_mu_parameters
    
    @property
    def u_serr_mu_parameters(self):
        """
        Element u_serr_mu_parameters ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 57
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__u_serr_mu_parameters(self._handle)
        if array_handle in self._arrays:
            u_serr_mu_parameters = self._arrays[array_handle]
        else:
            u_serr_mu_parameters = \
                f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__u_serr_mu_parameters)
            self._arrays[array_handle] = u_serr_mu_parameters
        return u_serr_mu_parameters
    
    @u_serr_mu_parameters.setter
    def u_serr_mu_parameters(self, u_serr_mu_parameters):
        self.u_serr_mu_parameters[...] = u_serr_mu_parameters
    
    @property
    def serr_sigma_parameters(self):
        """
        Element serr_sigma_parameters ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 58
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__serr_sigma_parameters(self._handle)
        if array_handle in self._arrays:
            serr_sigma_parameters = self._arrays[array_handle]
        else:
            serr_sigma_parameters = \
                f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__serr_sigma_parameters)
            self._arrays[array_handle] = serr_sigma_parameters
        return serr_sigma_parameters
    
    @serr_sigma_parameters.setter
    def serr_sigma_parameters(self, serr_sigma_parameters):
        self.serr_sigma_parameters[...] = serr_sigma_parameters
    
    @property
    def l_serr_sigma_parameters(self):
        """
        Element l_serr_sigma_parameters ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 59
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__l_serr_sigma_parameters(self._handle)
        if array_handle in self._arrays:
            l_serr_sigma_parameters = self._arrays[array_handle]
        else:
            l_serr_sigma_parameters = \
                f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__l_serr_sigma_parameters)
            self._arrays[array_handle] = l_serr_sigma_parameters
        return l_serr_sigma_parameters
    
    @l_serr_sigma_parameters.setter
    def l_serr_sigma_parameters(self, l_serr_sigma_parameters):
        self.l_serr_sigma_parameters[...] = l_serr_sigma_parameters
    
    @property
    def u_serr_sigma_parameters(self):
        """
        Element u_serr_sigma_parameters ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 line 60
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_optimize_optionsdt__array__u_serr_sigma_parameters(self._handle)
        if array_handle in self._arrays:
            u_serr_sigma_parameters = self._arrays[array_handle]
        else:
            u_serr_sigma_parameters = \
                f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_optimize_optionsdt__array__u_serr_sigma_parameters)
            self._arrays[array_handle] = u_serr_sigma_parameters
        return u_serr_sigma_parameters
    
    @u_serr_sigma_parameters.setter
    def u_serr_sigma_parameters(self, u_serr_sigma_parameters):
        self.u_serr_sigma_parameters[...] = u_serr_sigma_parameters
    
    
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
    

def optimize_optionsdt_copy(self):
    """
    this_copy = optimize_optionsdt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_optimize_options.f90 lines 98-102
    
    Parameters
    ----------
    this : Optimize_Optionsdt
    
    Returns
    -------
    this_copy : Optimize_Optionsdt
    
    """
    this_copy = \
        _libfcore.f90wrap_mwd_optimize_options__optimize_optionsdt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.Optimize_OptionsDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_optimize_options".')

for func in _dt_array_initialisers:
    func()

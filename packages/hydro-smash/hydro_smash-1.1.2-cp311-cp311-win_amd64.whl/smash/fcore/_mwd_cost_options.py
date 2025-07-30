"""
Module mwd_cost_options


Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 lines 34-101

(MWD) Module Wrapped and Differentiated.

Type
----

- Cost_OptionsDT
Cost options passed by user to define the output cost

======================== =======================================
`Variables`              Description
======================== =======================================
``bayesian``             Enable bayesian cost computation
``njoc``                 Number of jobs components
``jobs_cmpt``            Jobs components
``wjobs_cmpt``           Weight jobs components
``njrc``                 Number of jreg components
``wjreg``                Base weight for regularization
``jreg_cmpt``            Jreg components
``wjreg_cmpt``           Weight jreg components
``nog``                  Number of optimized gauges
``gauge``                Optimized gauges
``wgauge``               Weight optimized gauges
``end_warmup``           End Warmup index
``n_event ``             Number of flood events
``mask_event  ``         Mask info by segmentation algorithm
``control_prior``        Array of PriorType(from mwd_bayesian_tools)
======================== =======================================

Subroutine
----------

- Cost_OptionsDT_initialise
- Cost_OptionsDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore._f90wrap_decorator import f90wrap_getter_char_array, f90wrap_setter_char_array
from smash.fcore._f90wrap_decorator import f90wrap_getter_index, f90wrap_setter_index
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy
from smash.fcore._mwd_bayesian_tools import PriorType

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.Cost_OptionsDT")
class Cost_OptionsDT(f90wrap.runtime.FortranDerivedType):
    def alloc_control_prior(self, n, npar):
        return cost_optionsdt_alloc_control_prior(self, n, npar)
    def copy(self):
        return cost_optionsdt_copy(self)
    """
    Type(name=cost_optionsdt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 lines 40-56
    
    """
    def __init__(self, setup, mesh, njoc, njrc, handle=None):
        """
        self = Cost_Optionsdt(setup, mesh, njoc, njrc)
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 lines 59-84
        
        Parameters
        ----------
        setup : Setupdt
        mesh : Meshdt
        njoc : int
        njrc : int
        
        Returns
        -------
        this : Cost_Optionsdt
        
        only PriorType, PriorType_initialise
        only: sp, lchar
        only: SetupDT
        only: MeshDT
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = \
            _libfcore.f90wrap_mwd_cost_options__cost_optionsdt_initialise(setup=setup._handle, \
            mesh=mesh._handle, njoc=njoc, njrc=njrc)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Cost_Optionsdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 lines 40-56
        
        Parameters
        ----------
        this : Cost_Optionsdt
            Object to be destructed
        
        
        Automatically generated destructor for cost_optionsdt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_cost_options__cost_optionsdt_finalise(this=self._handle)
        except:
            pass
    
    @property
    def bayesian(self):
        """
        Element bayesian ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 41
        
        """
        return _libfcore.f90wrap_cost_optionsdt__get__bayesian(self._handle)
    
    @bayesian.setter
    def bayesian(self, bayesian):
        _libfcore.f90wrap_cost_optionsdt__set__bayesian(self._handle, bayesian)
    
    @property
    def njoc(self):
        """
        Element njoc ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 42
        
        """
        return _libfcore.f90wrap_cost_optionsdt__get__njoc(self._handle)
    
    @njoc.setter
    def njoc(self, njoc):
        _libfcore.f90wrap_cost_optionsdt__set__njoc(self._handle, njoc)
    
    @property
    @f90wrap_getter_char_array
    def jobs_cmpt(self):
        """
        Element jobs_cmpt ftype=character(lchar) pytype=str
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 43
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_cost_optionsdt__array__jobs_cmpt(self._handle)
        if array_handle in self._arrays:
            jobs_cmpt = self._arrays[array_handle]
        else:
            jobs_cmpt = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_cost_optionsdt__array__jobs_cmpt)
            self._arrays[array_handle] = jobs_cmpt
        return jobs_cmpt
    
    @jobs_cmpt.setter
    @f90wrap_setter_char_array
    def jobs_cmpt(self, jobs_cmpt):
        self.jobs_cmpt[...] = jobs_cmpt
    
    @property
    def wjobs_cmpt(self):
        """
        Element wjobs_cmpt ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 44
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_cost_optionsdt__array__wjobs_cmpt(self._handle)
        if array_handle in self._arrays:
            wjobs_cmpt = self._arrays[array_handle]
        else:
            wjobs_cmpt = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_cost_optionsdt__array__wjobs_cmpt)
            self._arrays[array_handle] = wjobs_cmpt
        return wjobs_cmpt
    
    @wjobs_cmpt.setter
    def wjobs_cmpt(self, wjobs_cmpt):
        self.wjobs_cmpt[...] = wjobs_cmpt
    
    @property
    @f90wrap_getter_char_array
    def jobs_cmpt_tfm(self):
        """
        Element jobs_cmpt_tfm ftype=character(lchar) pytype=str
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 45
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_cost_optionsdt__array__jobs_cmpt_tfm(self._handle)
        if array_handle in self._arrays:
            jobs_cmpt_tfm = self._arrays[array_handle]
        else:
            jobs_cmpt_tfm = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_cost_optionsdt__array__jobs_cmpt_tfm)
            self._arrays[array_handle] = jobs_cmpt_tfm
        return jobs_cmpt_tfm
    
    @jobs_cmpt_tfm.setter
    @f90wrap_setter_char_array
    def jobs_cmpt_tfm(self, jobs_cmpt_tfm):
        self.jobs_cmpt_tfm[...] = jobs_cmpt_tfm
    
    @property
    def njrc(self):
        """
        Element njrc ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 46
        
        """
        return _libfcore.f90wrap_cost_optionsdt__get__njrc(self._handle)
    
    @njrc.setter
    def njrc(self, njrc):
        _libfcore.f90wrap_cost_optionsdt__set__njrc(self._handle, njrc)
    
    @property
    def wjreg(self):
        """
        Element wjreg ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 47
        
        """
        return _libfcore.f90wrap_cost_optionsdt__get__wjreg(self._handle)
    
    @wjreg.setter
    def wjreg(self, wjreg):
        _libfcore.f90wrap_cost_optionsdt__set__wjreg(self._handle, wjreg)
    
    @property
    @f90wrap_getter_char_array
    def jreg_cmpt(self):
        """
        Element jreg_cmpt ftype=character(lchar) pytype=str
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 48
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_cost_optionsdt__array__jreg_cmpt(self._handle)
        if array_handle in self._arrays:
            jreg_cmpt = self._arrays[array_handle]
        else:
            jreg_cmpt = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_cost_optionsdt__array__jreg_cmpt)
            self._arrays[array_handle] = jreg_cmpt
        return jreg_cmpt
    
    @jreg_cmpt.setter
    @f90wrap_setter_char_array
    def jreg_cmpt(self, jreg_cmpt):
        self.jreg_cmpt[...] = jreg_cmpt
    
    @property
    def wjreg_cmpt(self):
        """
        Element wjreg_cmpt ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 49
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_cost_optionsdt__array__wjreg_cmpt(self._handle)
        if array_handle in self._arrays:
            wjreg_cmpt = self._arrays[array_handle]
        else:
            wjreg_cmpt = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_cost_optionsdt__array__wjreg_cmpt)
            self._arrays[array_handle] = wjreg_cmpt
        return wjreg_cmpt
    
    @wjreg_cmpt.setter
    def wjreg_cmpt(self, wjreg_cmpt):
        self.wjreg_cmpt[...] = wjreg_cmpt
    
    @property
    def nog(self):
        """
        Element nog ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 50
        
        """
        return _libfcore.f90wrap_cost_optionsdt__get__nog(self._handle)
    
    @nog.setter
    def nog(self, nog):
        _libfcore.f90wrap_cost_optionsdt__set__nog(self._handle, nog)
    
    @property
    def gauge(self):
        """
        Element gauge ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 51
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_cost_optionsdt__array__gauge(self._handle)
        if array_handle in self._arrays:
            gauge = self._arrays[array_handle]
        else:
            gauge = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_cost_optionsdt__array__gauge)
            self._arrays[array_handle] = gauge
        return gauge
    
    @gauge.setter
    def gauge(self, gauge):
        self.gauge[...] = gauge
    
    @property
    def wgauge(self):
        """
        Element wgauge ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 52
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_cost_optionsdt__array__wgauge(self._handle)
        if array_handle in self._arrays:
            wgauge = self._arrays[array_handle]
        else:
            wgauge = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_cost_optionsdt__array__wgauge)
            self._arrays[array_handle] = wgauge
        return wgauge
    
    @wgauge.setter
    def wgauge(self, wgauge):
        self.wgauge[...] = wgauge
    
    @property
    @f90wrap_getter_index
    def end_warmup(self):
        """
        Element end_warmup ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 53
        
        """
        return _libfcore.f90wrap_cost_optionsdt__get__end_warmup(self._handle)
    
    @end_warmup.setter
    @f90wrap_setter_index
    def end_warmup(self, end_warmup):
        _libfcore.f90wrap_cost_optionsdt__set__end_warmup(self._handle, end_warmup)
    
    @property
    def n_event(self):
        """
        Element n_event ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 54
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_cost_optionsdt__array__n_event(self._handle)
        if array_handle in self._arrays:
            n_event = self._arrays[array_handle]
        else:
            n_event = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_cost_optionsdt__array__n_event)
            self._arrays[array_handle] = n_event
        return n_event
    
    @n_event.setter
    def n_event(self, n_event):
        self.n_event[...] = n_event
    
    @property
    def mask_event(self):
        """
        Element mask_event ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 55
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_cost_optionsdt__array__mask_event(self._handle)
        if array_handle in self._arrays:
            mask_event = self._arrays[array_handle]
        else:
            mask_event = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_cost_optionsdt__array__mask_event)
            self._arrays[array_handle] = mask_event
        return mask_event
    
    @mask_event.setter
    def mask_event(self, mask_event):
        self.mask_event[...] = mask_event
    
    def init_array_control_prior(self):
        self.control_prior = f90wrap.runtime.FortranDerivedTypeArray(self,
                                        _libfcore.f90wrap_cost_optionsdt__array_getitem__control_prior,
                                        _libfcore.f90wrap_cost_optionsdt__array_setitem__control_prior,
                                        _libfcore.f90wrap_cost_optionsdt__array_len__control_prior,
                                        """
        Element control_prior ftype=type(priortype) pytype=Priortype
        
        
        Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 line 56
        
        """, PriorType)
        return self.control_prior
    
    
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
    
    
    _dt_array_initialisers = [init_array_control_prior]
    

def cost_optionsdt_copy(self):
    """
    this_copy = cost_optionsdt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 lines 86-90
    
    Parameters
    ----------
    this : Cost_Optionsdt
    
    Returns
    -------
    this_copy : Cost_Optionsdt
    
    """
    this_copy = \
        _libfcore.f90wrap_mwd_cost_options__cost_optionsdt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.Cost_OptionsDT").from_handle(this_copy, \
        alloc=True)
    return this_copy

def cost_optionsdt_alloc_control_prior(self, n, npar):
    """
    cost_optionsdt_alloc_control_prior(self, n, npar)
    
    
    Defined at ../smash/fcore/derived_type/mwd_cost_options.f90 lines 92-101
    
    Parameters
    ----------
    this : Cost_Optionsdt
    n : int
    npar : int array
    
    """
    _libfcore.f90wrap_mwd_cost_options__cost_optionsdt_alloc_control_prior(this=self._handle, \
        n=n, npar=npar)


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_cost_options".')

for func in _dt_array_initialisers:
    func()

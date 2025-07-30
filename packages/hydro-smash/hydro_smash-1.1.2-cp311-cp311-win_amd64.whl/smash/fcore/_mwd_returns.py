"""
Module mwd_returns


Defined at ../smash/fcore/derived_type/mwd_returns.f90 lines 37-123

(MWD) Module Wrapped and Differentiated.

Type
----

- ReturnsDT
Usefull quantities returned by the hydrological model other than response \
    variables themselves.

======================== =======================================
`Variables`              Description
======================== =======================================
``nmts``                 Number of time step to return
``mask_time_step``       Mask of time step
``rr_states``            Array of Rr_StatesDT
``rr_states_flag``       Return flag of rr_states
``q_domain``             Array of discharge
``q_domain_flag``        Return flag of q_domain
``cost``                 Cost value
``cost_flag``            Return flag of cost
``jobs``                 Jobs value
``jobs_flag``            Return flag of jobs
``jreg``                 Jreg value
``jreg_flag``            Return flag of jreg
``log_lkh``              Log_lkh value
``log_lkh_flag``         Return flag of log_lkh
``log_prior``            Log_prior value
``log_prior_flag``       Return flag of log_prior
``log_h``                Log_h value
``log_h_flag``           Return flag of log_h
======================== =======================================

Subroutine
----------

- ReturnsDT_initialise
- ReturnsDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore._f90wrap_decorator import f90wrap_getter_index_array, f90wrap_setter_index_array
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy
from smash.fcore._mwd_rr_states import RR_StatesDT

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.ReturnsDT")
class ReturnsDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return returnsdt_copy(self)
    """
    Type(name=returnsdt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_returns.f90 lines 43-64
    
    """
    def __init__(self, setup, mesh, nmts, keys, handle=None):
        """
        self = Returnsdt(setup, mesh, nmts, keys)
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 lines 67-117
        
        Parameters
        ----------
        setup : Setupdt
        mesh : Meshdt
        nmts : int
        keys : str array
        
        Returns
        -------
        this : Returnsdt
        
        only: sp
        only: SetupDT
        only: MeshDT
        only: RR_StatesDT, RR_StatesDT_initialise
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = \
            _libfcore.f90wrap_mwd_returns__returnsdt_initialise(setup=setup._handle, \
            mesh=mesh._handle, nmts=nmts, keys=keys)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Returnsdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 lines 43-64
        
        Parameters
        ----------
        this : Returnsdt
            Object to be destructed
        
        
        Automatically generated destructor for returnsdt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_returns__returnsdt_finalise(this=self._handle)
        except:
            pass
    
    @property
    def nmts(self):
        """
        Element nmts ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 44
        
        """
        return _libfcore.f90wrap_returnsdt__get__nmts(self._handle)
    
    @nmts.setter
    def nmts(self, nmts):
        _libfcore.f90wrap_returnsdt__set__nmts(self._handle, nmts)
    
    @property
    def mask_time_step(self):
        """
        Element mask_time_step ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 45
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_returnsdt__array__mask_time_step(self._handle)
        if array_handle in self._arrays:
            mask_time_step = self._arrays[array_handle]
        else:
            mask_time_step = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_returnsdt__array__mask_time_step)
            self._arrays[array_handle] = mask_time_step
        return mask_time_step
    
    @mask_time_step.setter
    def mask_time_step(self, mask_time_step):
        self.mask_time_step[...] = mask_time_step
    
    @property
    @f90wrap_getter_index_array
    def time_step_to_returns_time_step(self):
        """
        Element time_step_to_returns_time_step ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 46
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_returnsdt__array__time_step_to_returns_time_step(self._handle)
        if array_handle in self._arrays:
            time_step_to_returns_time_step = self._arrays[array_handle]
        else:
            time_step_to_returns_time_step = \
                f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_returnsdt__array__time_step_to_returns_time_step)
            self._arrays[array_handle] = time_step_to_returns_time_step
        return time_step_to_returns_time_step
    
    @time_step_to_returns_time_step.setter
    @f90wrap_setter_index_array
    def time_step_to_returns_time_step(self, time_step_to_returns_time_step):
        self.time_step_to_returns_time_step[...] = time_step_to_returns_time_step
    
    def init_array_rr_states(self):
        self.rr_states = f90wrap.runtime.FortranDerivedTypeArray(self,
                                        _libfcore.f90wrap_returnsdt__array_getitem__rr_states,
                                        _libfcore.f90wrap_returnsdt__array_setitem__rr_states,
                                        _libfcore.f90wrap_returnsdt__array_len__rr_states,
                                        """
        Element rr_states ftype=type(rr_statesdt) pytype=Rr_Statesdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 47
        
        """, RR_StatesDT)
        return self.rr_states
    
    @property
    def rr_states_flag(self):
        """
        Element rr_states_flag ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 48
        
        """
        return _libfcore.f90wrap_returnsdt__get__rr_states_flag(self._handle)
    
    @rr_states_flag.setter
    def rr_states_flag(self, rr_states_flag):
        _libfcore.f90wrap_returnsdt__set__rr_states_flag(self._handle, rr_states_flag)
    
    @property
    def q_domain(self):
        """
        Element q_domain ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 49
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_returnsdt__array__q_domain(self._handle)
        if array_handle in self._arrays:
            q_domain = self._arrays[array_handle]
        else:
            q_domain = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_returnsdt__array__q_domain)
            self._arrays[array_handle] = q_domain
        return q_domain
    
    @q_domain.setter
    def q_domain(self, q_domain):
        self.q_domain[...] = q_domain
    
    @property
    def q_domain_flag(self):
        """
        Element q_domain_flag ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 50
        
        """
        return _libfcore.f90wrap_returnsdt__get__q_domain_flag(self._handle)
    
    @q_domain_flag.setter
    def q_domain_flag(self, q_domain_flag):
        _libfcore.f90wrap_returnsdt__set__q_domain_flag(self._handle, q_domain_flag)
    
    @property
    def cost(self):
        """
        Element cost ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 51
        
        """
        return _libfcore.f90wrap_returnsdt__get__cost(self._handle)
    
    @cost.setter
    def cost(self, cost):
        _libfcore.f90wrap_returnsdt__set__cost(self._handle, cost)
    
    @property
    def cost_flag(self):
        """
        Element cost_flag ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 52
        
        """
        return _libfcore.f90wrap_returnsdt__get__cost_flag(self._handle)
    
    @cost_flag.setter
    def cost_flag(self, cost_flag):
        _libfcore.f90wrap_returnsdt__set__cost_flag(self._handle, cost_flag)
    
    @property
    def jobs(self):
        """
        Element jobs ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 53
        
        """
        return _libfcore.f90wrap_returnsdt__get__jobs(self._handle)
    
    @jobs.setter
    def jobs(self, jobs):
        _libfcore.f90wrap_returnsdt__set__jobs(self._handle, jobs)
    
    @property
    def jobs_flag(self):
        """
        Element jobs_flag ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 54
        
        """
        return _libfcore.f90wrap_returnsdt__get__jobs_flag(self._handle)
    
    @jobs_flag.setter
    def jobs_flag(self, jobs_flag):
        _libfcore.f90wrap_returnsdt__set__jobs_flag(self._handle, jobs_flag)
    
    @property
    def jreg(self):
        """
        Element jreg ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 55
        
        """
        return _libfcore.f90wrap_returnsdt__get__jreg(self._handle)
    
    @jreg.setter
    def jreg(self, jreg):
        _libfcore.f90wrap_returnsdt__set__jreg(self._handle, jreg)
    
    @property
    def jreg_flag(self):
        """
        Element jreg_flag ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 56
        
        """
        return _libfcore.f90wrap_returnsdt__get__jreg_flag(self._handle)
    
    @jreg_flag.setter
    def jreg_flag(self, jreg_flag):
        _libfcore.f90wrap_returnsdt__set__jreg_flag(self._handle, jreg_flag)
    
    @property
    def log_lkh(self):
        """
        Element log_lkh ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 57
        
        """
        return _libfcore.f90wrap_returnsdt__get__log_lkh(self._handle)
    
    @log_lkh.setter
    def log_lkh(self, log_lkh):
        _libfcore.f90wrap_returnsdt__set__log_lkh(self._handle, log_lkh)
    
    @property
    def log_lkh_flag(self):
        """
        Element log_lkh_flag ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 58
        
        """
        return _libfcore.f90wrap_returnsdt__get__log_lkh_flag(self._handle)
    
    @log_lkh_flag.setter
    def log_lkh_flag(self, log_lkh_flag):
        _libfcore.f90wrap_returnsdt__set__log_lkh_flag(self._handle, log_lkh_flag)
    
    @property
    def log_prior(self):
        """
        Element log_prior ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 59
        
        """
        return _libfcore.f90wrap_returnsdt__get__log_prior(self._handle)
    
    @log_prior.setter
    def log_prior(self, log_prior):
        _libfcore.f90wrap_returnsdt__set__log_prior(self._handle, log_prior)
    
    @property
    def log_prior_flag(self):
        """
        Element log_prior_flag ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 60
        
        """
        return _libfcore.f90wrap_returnsdt__get__log_prior_flag(self._handle)
    
    @log_prior_flag.setter
    def log_prior_flag(self, log_prior_flag):
        _libfcore.f90wrap_returnsdt__set__log_prior_flag(self._handle, log_prior_flag)
    
    @property
    def log_h(self):
        """
        Element log_h ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 61
        
        """
        return _libfcore.f90wrap_returnsdt__get__log_h(self._handle)
    
    @log_h.setter
    def log_h(self, log_h):
        _libfcore.f90wrap_returnsdt__set__log_h(self._handle, log_h)
    
    @property
    def log_h_flag(self):
        """
        Element log_h_flag ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 62
        
        """
        return _libfcore.f90wrap_returnsdt__get__log_h_flag(self._handle)
    
    @log_h_flag.setter
    def log_h_flag(self, log_h_flag):
        _libfcore.f90wrap_returnsdt__set__log_h_flag(self._handle, log_h_flag)
    
    @property
    def internal_fluxes(self):
        """
        Element internal_fluxes ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 63
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_returnsdt__array__internal_fluxes(self._handle)
        if array_handle in self._arrays:
            internal_fluxes = self._arrays[array_handle]
        else:
            internal_fluxes = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_returnsdt__array__internal_fluxes)
            self._arrays[array_handle] = internal_fluxes
        return internal_fluxes
    
    @internal_fluxes.setter
    def internal_fluxes(self, internal_fluxes):
        self.internal_fluxes[...] = internal_fluxes
    
    @property
    def internal_fluxes_flag(self):
        """
        Element internal_fluxes_flag ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_returns.f90 line 64
        
        """
        return _libfcore.f90wrap_returnsdt__get__internal_fluxes_flag(self._handle)
    
    @internal_fluxes_flag.setter
    def internal_fluxes_flag(self, internal_fluxes_flag):
        _libfcore.f90wrap_returnsdt__set__internal_fluxes_flag(self._handle, \
            internal_fluxes_flag)
    
    
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
    
    
    _dt_array_initialisers = [init_array_rr_states]
    

def returnsdt_copy(self):
    """
    this_copy = returnsdt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_returns.f90 lines 119-123
    
    Parameters
    ----------
    this : Returnsdt
    
    Returns
    -------
    this_copy : Returnsdt
    
    """
    this_copy = _libfcore.f90wrap_mwd_returns__returnsdt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.ReturnsDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_returns".')

for func in _dt_array_initialisers:
    func()

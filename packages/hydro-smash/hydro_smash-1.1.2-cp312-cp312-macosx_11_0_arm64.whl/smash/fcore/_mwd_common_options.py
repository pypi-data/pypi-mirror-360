"""
Module mwd_common_options


Defined at ../smash/fcore/derived_type/mwd_common_options.f90 lines 21-36

(MWD) Module Wrapped and Differentiated.

Type
----

- Common_OptionsDT
Common options passed by user

======================== =======================================
`Variables`              Description
======================== =======================================
``ncpu``                 Number of CPUs(default: 1)
``verbose``              Enable verbose(default: .true.)
======================== =======================================

Subroutine
----------

- Common_OptionsDT_initialise
- Common_OptionsDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.Common_OptionsDT")
class Common_OptionsDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return common_optionsdt_copy(self)
    """
    Type(name=common_optionsdt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_common_options.f90 lines 23-25
    
    """
    def __init__(self, handle=None):
        """
        self = Common_Optionsdt()
        
        
        Defined at ../smash/fcore/derived_type/mwd_common_options.f90 lines 28-30
        
        
        Returns
        -------
        this : Common_Optionsdt
        
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = _libfcore.f90wrap_mwd_common_options__common_optionsdt_initialise()
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Common_Optionsdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_common_options.f90 lines 23-25
        
        Parameters
        ----------
        this : Common_Optionsdt
            Object to be destructed
        
        
        Automatically generated destructor for common_optionsdt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_common_options__common_optionsdt_finalise(this=self._handle)
        except:
            pass
    
    @property
    def ncpu(self):
        """
        Element ncpu ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_common_options.f90 line 24
        
        """
        return _libfcore.f90wrap_common_optionsdt__get__ncpu(self._handle)
    
    @ncpu.setter
    def ncpu(self, ncpu):
        _libfcore.f90wrap_common_optionsdt__set__ncpu(self._handle, ncpu)
    
    @property
    def verbose(self):
        """
        Element verbose ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_common_options.f90 line 25
        
        """
        return _libfcore.f90wrap_common_optionsdt__get__verbose(self._handle)
    
    @verbose.setter
    def verbose(self, verbose):
        _libfcore.f90wrap_common_optionsdt__set__verbose(self._handle, verbose)
    
    
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
    

def common_optionsdt_copy(self):
    """
    this_copy = common_optionsdt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_common_options.f90 lines 32-36
    
    Parameters
    ----------
    this : Common_Optionsdt
    
    Returns
    -------
    this_copy : Common_Optionsdt
    
    """
    this_copy = \
        _libfcore.f90wrap_mwd_common_options__common_optionsdt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.Common_OptionsDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_common_options".')

for func in _dt_array_initialisers:
    func()

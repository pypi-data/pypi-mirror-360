"""
Module mwd_output


Defined at ../smash/fcore/derived_type/mwd_output.f90 lines 21-46

(MWD) Module Wrapped and Differentiated.

Type
----

- OutputDT

======================== =======================================
`Variables`              Description
======================== =======================================
``cost``                 Value of cost function
``response``             ResponseDT
``rr_final_states``      Rr_StatesDT
======================== =======================================

Subroutine
----------

- OutputDT_initialise
- OutputDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy
from smash.fcore._mwd_rr_states import RR_StatesDT
from smash.fcore._mwd_response import ResponseDT

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.OutputDT")
class OutputDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return outputdt_copy(self)
    """
    Type(name=outputdt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_output.f90 lines 28-31
    
    """
    def __init__(self, setup, mesh, handle=None):
        """
        self = Outputdt(setup, mesh)
        
        
        Defined at ../smash/fcore/derived_type/mwd_output.f90 lines 34-40
        
        Parameters
        ----------
        setup : Setupdt
        mesh : Meshdt
        
        Returns
        -------
        this : Outputdt
        
        only: sp
        only: SetupDT
        only: MeshDT
        only: ResponseDT, ResponseDT_initialise
        only: Rr_StatesDT, Rr_StatesDT_initialise
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = _libfcore.f90wrap_mwd_output__outputdt_initialise(setup=setup._handle, \
            mesh=mesh._handle)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Outputdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_output.f90 lines 28-31
        
        Parameters
        ----------
        this : Outputdt
            Object to be destructed
        
        
        Automatically generated destructor for outputdt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_output__outputdt_finalise(this=self._handle)
        except:
            pass
    
    @property
    def response(self):
        """
        Element response ftype=type(responsedt) pytype=Responsedt
        
        
        Defined at ../smash/fcore/derived_type/mwd_output.f90 line 29
        
        """
        response_handle = _libfcore.f90wrap_outputdt__get__response(self._handle)
        if tuple(response_handle) in self._objs:
            response = self._objs[tuple(response_handle)]
        else:
            response = ResponseDT.from_handle(response_handle)
            self._objs[tuple(response_handle)] = response
        return response
    
    @response.setter
    def response(self, response):
        response = response._handle
        _libfcore.f90wrap_outputdt__set__response(self._handle, response)
    
    @property
    def rr_final_states(self):
        """
        Element rr_final_states ftype=type(rr_statesdt) pytype=Rr_Statesdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_output.f90 line 30
        
        """
        rr_final_states_handle = \
            _libfcore.f90wrap_outputdt__get__rr_final_states(self._handle)
        if tuple(rr_final_states_handle) in self._objs:
            rr_final_states = self._objs[tuple(rr_final_states_handle)]
        else:
            rr_final_states = RR_StatesDT.from_handle(rr_final_states_handle)
            self._objs[tuple(rr_final_states_handle)] = rr_final_states
        return rr_final_states
    
    @rr_final_states.setter
    def rr_final_states(self, rr_final_states):
        rr_final_states = rr_final_states._handle
        _libfcore.f90wrap_outputdt__set__rr_final_states(self._handle, rr_final_states)
    
    @property
    def cost(self):
        """
        Element cost ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_output.f90 line 31
        
        """
        return _libfcore.f90wrap_outputdt__get__cost(self._handle)
    
    @cost.setter
    def cost(self, cost):
        _libfcore.f90wrap_outputdt__set__cost(self._handle, cost)
    
    
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
    

def outputdt_copy(self):
    """
    this_copy = outputdt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_output.f90 lines 42-46
    
    Parameters
    ----------
    this : Outputdt
    
    Returns
    -------
    this_copy : Outputdt
    
    """
    this_copy = _libfcore.f90wrap_mwd_output__outputdt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.OutputDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module "mwd_output".')

for func in _dt_array_initialisers:
    func()

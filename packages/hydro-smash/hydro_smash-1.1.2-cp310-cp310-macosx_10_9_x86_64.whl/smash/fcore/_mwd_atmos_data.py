"""
Module mwd_atmos_data


Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 lines 31-95

(MWD) Module Wrapped and Differentiated.

Type
----

- Atmos_DataDT
Atmospheric data used to force smash and derived quantities.

======================== =======================================
`Variables`              Description
======================== =======================================
``prcp``                 Precipitation field                         [mm]
``pet``                  Potential evapotranspiration field          [mm]
``snow``                 Snow field                                  [mm]
``temp``                 Temperature field                           [C]
``sparse_prcp``          Sparse precipitation field                  [mm]
``sparse_pet``           Sparse potential evapotranspiration field   [mm]
``sparse_snow``          Sparse snow field                           [mm]
``sparse_temp``          Sparse temperature field                    [C]
``mean_prcp``            Mean precipitation at gauge                 [mm]
``mean_pet``             Mean potential evapotranspiration at gauge  [mm]
``mean_snow``            Mean snow at gauge                          [mm]
``mean_temp``            Mean temperature at gauge                   [C]
======================== =======================================

Subroutine
----------

- Atmos_DataDT_initialise
- Atmos_DataDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy
from smash.fcore._mwd_sparse_matrix import Sparse_MatrixDT

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.Atmos_DataDT")
class Atmos_DataDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return atmos_datadt_copy(self)
    """
    Type(name=atmos_datadt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 lines 37-49
    
    """
    def __init__(self, setup, mesh, handle=None):
        """
        self = Atmos_Datadt(setup, mesh)
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 lines 52-89
        
        Parameters
        ----------
        setup : Setupdt
        mesh : Meshdt
        
        Returns
        -------
        this : Atmos_Datadt
        
        only: sp
        only: SetupDT
        only: MeshDT
        only: Sparse_MatrixDT, Sparse_MatrixDT_initialise_array
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = \
            _libfcore.f90wrap_mwd_atmos_data__atmos_datadt_initialise(setup=setup._handle, \
            mesh=mesh._handle)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Atmos_Datadt
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 lines 37-49
        
        Parameters
        ----------
        this : Atmos_Datadt
            Object to be destructed
        
        
        Automatically generated destructor for atmos_datadt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_atmos_data__atmos_datadt_finalise(this=self._handle)
        except:
            pass
    
    @property
    def prcp(self):
        """
        Element prcp ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 38
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_atmos_datadt__array__prcp(self._handle)
        if array_handle in self._arrays:
            prcp = self._arrays[array_handle]
        else:
            prcp = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_atmos_datadt__array__prcp)
            self._arrays[array_handle] = prcp
        return prcp
    
    @prcp.setter
    def prcp(self, prcp):
        self.prcp[...] = prcp
    
    @property
    def pet(self):
        """
        Element pet ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 39
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_atmos_datadt__array__pet(self._handle)
        if array_handle in self._arrays:
            pet = self._arrays[array_handle]
        else:
            pet = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_atmos_datadt__array__pet)
            self._arrays[array_handle] = pet
        return pet
    
    @pet.setter
    def pet(self, pet):
        self.pet[...] = pet
    
    @property
    def snow(self):
        """
        Element snow ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 40
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_atmos_datadt__array__snow(self._handle)
        if array_handle in self._arrays:
            snow = self._arrays[array_handle]
        else:
            snow = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_atmos_datadt__array__snow)
            self._arrays[array_handle] = snow
        return snow
    
    @snow.setter
    def snow(self, snow):
        self.snow[...] = snow
    
    @property
    def temp(self):
        """
        Element temp ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 41
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_atmos_datadt__array__temp(self._handle)
        if array_handle in self._arrays:
            temp = self._arrays[array_handle]
        else:
            temp = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_atmos_datadt__array__temp)
            self._arrays[array_handle] = temp
        return temp
    
    @temp.setter
    def temp(self, temp):
        self.temp[...] = temp
    
    def init_array_sparse_prcp(self):
        self.sparse_prcp = f90wrap.runtime.FortranDerivedTypeArray(self,
                                        _libfcore.f90wrap_atmos_datadt__array_getitem__sparse_prcp,
                                        _libfcore.f90wrap_atmos_datadt__array_setitem__sparse_prcp,
                                        _libfcore.f90wrap_atmos_datadt__array_len__sparse_prcp,
                                        """
        Element sparse_prcp ftype=type(sparse_matrixdt) pytype=Sparse_Matrixdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 42
        
        """, Sparse_MatrixDT)
        return self.sparse_prcp
    
    def init_array_sparse_pet(self):
        self.sparse_pet = f90wrap.runtime.FortranDerivedTypeArray(self,
                                        _libfcore.f90wrap_atmos_datadt__array_getitem__sparse_pet,
                                        _libfcore.f90wrap_atmos_datadt__array_setitem__sparse_pet,
                                        _libfcore.f90wrap_atmos_datadt__array_len__sparse_pet,
                                        """
        Element sparse_pet ftype=type(sparse_matrixdt) pytype=Sparse_Matrixdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 43
        
        """, Sparse_MatrixDT)
        return self.sparse_pet
    
    def init_array_sparse_snow(self):
        self.sparse_snow = f90wrap.runtime.FortranDerivedTypeArray(self,
                                        _libfcore.f90wrap_atmos_datadt__array_getitem__sparse_snow,
                                        _libfcore.f90wrap_atmos_datadt__array_setitem__sparse_snow,
                                        _libfcore.f90wrap_atmos_datadt__array_len__sparse_snow,
                                        """
        Element sparse_snow ftype=type(sparse_matrixdt) pytype=Sparse_Matrixdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 44
        
        """, Sparse_MatrixDT)
        return self.sparse_snow
    
    def init_array_sparse_temp(self):
        self.sparse_temp = f90wrap.runtime.FortranDerivedTypeArray(self,
                                        _libfcore.f90wrap_atmos_datadt__array_getitem__sparse_temp,
                                        _libfcore.f90wrap_atmos_datadt__array_setitem__sparse_temp,
                                        _libfcore.f90wrap_atmos_datadt__array_len__sparse_temp,
                                        """
        Element sparse_temp ftype=type(sparse_matrixdt) pytype=Sparse_Matrixdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 45
        
        """, Sparse_MatrixDT)
        return self.sparse_temp
    
    @property
    def mean_prcp(self):
        """
        Element mean_prcp ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 46
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_atmos_datadt__array__mean_prcp(self._handle)
        if array_handle in self._arrays:
            mean_prcp = self._arrays[array_handle]
        else:
            mean_prcp = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_atmos_datadt__array__mean_prcp)
            self._arrays[array_handle] = mean_prcp
        return mean_prcp
    
    @mean_prcp.setter
    def mean_prcp(self, mean_prcp):
        self.mean_prcp[...] = mean_prcp
    
    @property
    def mean_pet(self):
        """
        Element mean_pet ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 47
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_atmos_datadt__array__mean_pet(self._handle)
        if array_handle in self._arrays:
            mean_pet = self._arrays[array_handle]
        else:
            mean_pet = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_atmos_datadt__array__mean_pet)
            self._arrays[array_handle] = mean_pet
        return mean_pet
    
    @mean_pet.setter
    def mean_pet(self, mean_pet):
        self.mean_pet[...] = mean_pet
    
    @property
    def mean_snow(self):
        """
        Element mean_snow ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 48
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_atmos_datadt__array__mean_snow(self._handle)
        if array_handle in self._arrays:
            mean_snow = self._arrays[array_handle]
        else:
            mean_snow = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_atmos_datadt__array__mean_snow)
            self._arrays[array_handle] = mean_snow
        return mean_snow
    
    @mean_snow.setter
    def mean_snow(self, mean_snow):
        self.mean_snow[...] = mean_snow
    
    @property
    def mean_temp(self):
        """
        Element mean_temp ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 line 49
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_atmos_datadt__array__mean_temp(self._handle)
        if array_handle in self._arrays:
            mean_temp = self._arrays[array_handle]
        else:
            mean_temp = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_atmos_datadt__array__mean_temp)
            self._arrays[array_handle] = mean_temp
        return mean_temp
    
    @mean_temp.setter
    def mean_temp(self, mean_temp):
        self.mean_temp[...] = mean_temp
    
    
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
    
    
    _dt_array_initialisers = [init_array_sparse_prcp, init_array_sparse_pet, \
        init_array_sparse_snow, init_array_sparse_temp]
    

def atmos_datadt_copy(self):
    """
    this_copy = atmos_datadt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_atmos_data.f90 lines 91-95
    
    Parameters
    ----------
    this : Atmos_Datadt
    
    Returns
    -------
    this_copy : Atmos_Datadt
    
    """
    this_copy = \
        _libfcore.f90wrap_mwd_atmos_data__atmos_datadt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.Atmos_DataDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_atmos_data".')

for func in _dt_array_initialisers:
    func()

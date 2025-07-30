"""
Module mwd_sparse_matrix


Defined at ../smash/fcore/derived_type/mwd_sparse_matrix.f90 lines 25-84

(MWD) Module Wrapped and Differentiated.

Type
----

- Sparse_MatrixDT
Sparse matrices handling atmospheric data(prcp, pet, snow ...)
See COO matrices(google, scipy)

======================== =======================================
`Variables`              Description
======================== =======================================
``n``                    Number of data stored
``coo_fmt``              Sparse Matrix in COO format(default: .true.)
``zvalue``               Non stored value(default: 0)
``indices``              Indices of the sparse matrix
``values``               Values of the sparse matrix
======================== =======================================

Subroutine
----------

- Sparse_MatrixDT_initialise
- Sparse_MatrixDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.Sparse_MatrixDT")
class Sparse_MatrixDT(f90wrap.runtime.FortranDerivedType):
    def copy(self, this_copy):
        return sparse_matrixdt_copy(self, this_copy)
    def alloc(self, n, coo_fmt, zvalue):
        return sparse_matrixdt_alloc(self, n, coo_fmt, zvalue)
    """
    Type(name=sparse_matrixdt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_sparse_matrix.f90 lines 28-33
    
    """
    def __init__(self, n, coo_fmt, zvalue, handle=None):
        """
        self = Sparse_Matrixdt(n, coo_fmt, zvalue)
        
        
        Defined at ../smash/fcore/derived_type/mwd_sparse_matrix.f90 lines 36-51
        
        Parameters
        ----------
        n : int
        coo_fmt : bool
        zvalue : float
        
        Returns
        -------
        this : Sparse_Matrixdt
        
        only: sp
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = _libfcore.f90wrap_mwd_sparse_matrix__sparse_matrixdt_initialise(n=n, \
            coo_fmt=coo_fmt, zvalue=zvalue)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Sparse_Matrixdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_sparse_matrix.f90 lines 53-57
        
        Parameters
        ----------
        this : Sparse_Matrixdt
        
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_sparse_matrix__sparse_matrixdt_finalise(this=self._handle)
        except:
            pass
    
    @property
    def n(self):
        """
        Element n ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_sparse_matrix.f90 line 29
        
        """
        return _libfcore.f90wrap_sparse_matrixdt__get__n(self._handle)
    
    @n.setter
    def n(self, n):
        _libfcore.f90wrap_sparse_matrixdt__set__n(self._handle, n)
    
    @property
    def coo_fmt(self):
        """
        Element coo_fmt ftype=logical pytype=bool
        
        
        Defined at ../smash/fcore/derived_type/mwd_sparse_matrix.f90 line 30
        
        """
        return _libfcore.f90wrap_sparse_matrixdt__get__coo_fmt(self._handle)
    
    @coo_fmt.setter
    def coo_fmt(self, coo_fmt):
        _libfcore.f90wrap_sparse_matrixdt__set__coo_fmt(self._handle, coo_fmt)
    
    @property
    def zvalue(self):
        """
        Element zvalue ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_sparse_matrix.f90 line 31
        
        """
        return _libfcore.f90wrap_sparse_matrixdt__get__zvalue(self._handle)
    
    @zvalue.setter
    def zvalue(self, zvalue):
        _libfcore.f90wrap_sparse_matrixdt__set__zvalue(self._handle, zvalue)
    
    @property
    def indices(self):
        """
        Element indices ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_sparse_matrix.f90 line 32
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_sparse_matrixdt__array__indices(self._handle)
        if array_handle in self._arrays:
            indices = self._arrays[array_handle]
        else:
            indices = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_sparse_matrixdt__array__indices)
            self._arrays[array_handle] = indices
        return indices
    
    @indices.setter
    def indices(self, indices):
        self.indices[...] = indices
    
    @property
    def values(self):
        """
        Element values ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_sparse_matrix.f90 line 33
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_sparse_matrixdt__array__values(self._handle)
        if array_handle in self._arrays:
            values = self._arrays[array_handle]
        else:
            values = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_sparse_matrixdt__array__values)
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
    

def sparse_matrixdt_alloc(self, n, coo_fmt, zvalue):
    """
    sparse_matrixdt_alloc(self, n, coo_fmt, zvalue)
    
    
    Defined at ../smash/fcore/derived_type/mwd_sparse_matrix.f90 lines 72-78
    
    Parameters
    ----------
    this : Sparse_Matrixdt
    n : int
    coo_fmt : bool
    zvalue : float
    
    """
    _libfcore.f90wrap_mwd_sparse_matrix__sparse_matrixdt_alloc(this=self._handle, \
        n=n, coo_fmt=coo_fmt, zvalue=zvalue)

def sparse_matrixdt_copy(self, this_copy):
    """
    sparse_matrixdt_copy(self, this_copy)
    
    
    Defined at ../smash/fcore/derived_type/mwd_sparse_matrix.f90 lines 80-84
    
    Parameters
    ----------
    this : Sparse_Matrixdt
    this_copy : Sparse_Matrixdt
    
    """
    _libfcore.f90wrap_mwd_sparse_matrix__sparse_matrixdt_copy(this=self._handle, \
        this_copy=this_copy._handle)


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module \
        "mwd_sparse_matrix".')

for func in _dt_array_initialisers:
    func()

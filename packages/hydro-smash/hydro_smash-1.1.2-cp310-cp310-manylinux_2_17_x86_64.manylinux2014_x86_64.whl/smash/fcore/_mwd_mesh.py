"""
Module mwd_mesh


Defined at ../smash/fcore/derived_type/mwd_mesh.f90 lines 43-125

(MWD) Module Wrapped and Differentiated.

Type
----

- MeshDT
Meshing data

======================== =======================================
`Variables`              Description
======================== =======================================
``xres`` X cell size derived from flwdir [m / degree]
``yres`` Y cell size derived from flwdir [m / degree]
``xmin`` X mininimum value derived from flwdir [m / degree]
``ymax`` Y maximum value derived from flwdir [m / degree]
``nrow``                 Number of rows
``ncol``                 Number of columns
``dx`` X cells size(meter approximation) [m]
``dy`` Y cells size(meter approximation) [m]
``flwdir``               Flow directions
``flwacc`` Flow accumulation [m2]
``flwdst`` Flow distances from main outlet(s) [m]
``npar``                 Number of partition
``ncpar``                Number of cells per partition
``cscpar``               Cumulative sum of cells per partition
``cpar_to_rowcol``       Matrix linking partition cell(c) to(row, col)
``flwpar``               Flow partitions
``nac``                  Number of active cell
``active_cell``          Mask of active cell
``ng``                   Number of gauge
``gauge_pos``            Gauge position
``code``                 Gauge code
``area`` Drained area at gauge position [m2]
``area_dln`` Drained area at gauge position delineated [m2]
``rowcol_to_ind_ac`` Matrix linking(row, col) couple to active cell indice(k)
``local_active_cell``    Mask of local active cells

Subroutine
----------

- MeshDT_initialise
- MeshDT_copy
"""
from __future__ import print_function, absolute_import, division
from smash.fcore._f90wrap_decorator import f90wrap_getter_char_array, f90wrap_setter_char_array
from smash.fcore._f90wrap_decorator import f90wrap_getter_index_array, f90wrap_setter_index_array
from smash.fcore import _libfcore
import f90wrap.runtime
import logging
import numpy

_arrays = {}
_objs = {}

@f90wrap.runtime.register_class("libfcore.MeshDT")
class MeshDT(f90wrap.runtime.FortranDerivedType):
    def copy(self):
        return meshdt_copy(self)
    """
    Type(name=meshdt)
    
    
    Defined at ../smash/fcore/derived_type/mwd_mesh.f90 lines 47-72
    
    """
    def __init__(self, setup, nrow, ncol, npar, ng, handle=None):
        """
        self = Meshdt(setup, nrow, ncol, npar, ng)
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 lines 75-119
        
        Parameters
        ----------
        setup : Setupdt
        nrow : int
        ncol : int
        npar : int
        ng : int
        
        Returns
        -------
        this : Meshdt
        
        only: sp
        only: SetupDT
        """
        f90wrap.runtime.FortranDerivedType.__init__(self)
        result = _libfcore.f90wrap_mwd_mesh__meshdt_initialise(setup=setup._handle, \
            nrow=nrow, ncol=ncol, npar=npar, ng=ng)
        self._handle = result[0] if isinstance(result, tuple) else result
    
    def __del__(self):
        """
        Destructor for class Meshdt
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 lines 47-72
        
        Parameters
        ----------
        this : Meshdt
            Object to be destructed
        
        
        Automatically generated destructor for meshdt
        """
        try:
            if self._alloc:
                _libfcore.f90wrap_mwd_mesh__meshdt_finalise(this=self._handle)
        except:
            pass
    
    @property
    def xres(self):
        """
        Element xres ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 48
        
        """
        return _libfcore.f90wrap_meshdt__get__xres(self._handle)
    
    @xres.setter
    def xres(self, xres):
        _libfcore.f90wrap_meshdt__set__xres(self._handle, xres)
    
    @property
    def yres(self):
        """
        Element yres ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 49
        
        """
        return _libfcore.f90wrap_meshdt__get__yres(self._handle)
    
    @yres.setter
    def yres(self, yres):
        _libfcore.f90wrap_meshdt__set__yres(self._handle, yres)
    
    @property
    def xmin(self):
        """
        Element xmin ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 50
        
        """
        return _libfcore.f90wrap_meshdt__get__xmin(self._handle)
    
    @xmin.setter
    def xmin(self, xmin):
        _libfcore.f90wrap_meshdt__set__xmin(self._handle, xmin)
    
    @property
    def ymax(self):
        """
        Element ymax ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 51
        
        """
        return _libfcore.f90wrap_meshdt__get__ymax(self._handle)
    
    @ymax.setter
    def ymax(self, ymax):
        _libfcore.f90wrap_meshdt__set__ymax(self._handle, ymax)
    
    @property
    def nrow(self):
        """
        Element nrow ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 52
        
        """
        return _libfcore.f90wrap_meshdt__get__nrow(self._handle)
    
    @nrow.setter
    def nrow(self, nrow):
        _libfcore.f90wrap_meshdt__set__nrow(self._handle, nrow)
    
    @property
    def ncol(self):
        """
        Element ncol ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 53
        
        """
        return _libfcore.f90wrap_meshdt__get__ncol(self._handle)
    
    @ncol.setter
    def ncol(self, ncol):
        _libfcore.f90wrap_meshdt__set__ncol(self._handle, ncol)
    
    @property
    def dx(self):
        """
        Element dx ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 54
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__dx(self._handle)
        if array_handle in self._arrays:
            dx = self._arrays[array_handle]
        else:
            dx = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__dx)
            self._arrays[array_handle] = dx
        return dx
    
    @dx.setter
    def dx(self, dx):
        self.dx[...] = dx
    
    @property
    def dy(self):
        """
        Element dy ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 55
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__dy(self._handle)
        if array_handle in self._arrays:
            dy = self._arrays[array_handle]
        else:
            dy = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__dy)
            self._arrays[array_handle] = dy
        return dy
    
    @dy.setter
    def dy(self, dy):
        self.dy[...] = dy
    
    @property
    def flwdir(self):
        """
        Element flwdir ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 56
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__flwdir(self._handle)
        if array_handle in self._arrays:
            flwdir = self._arrays[array_handle]
        else:
            flwdir = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__flwdir)
            self._arrays[array_handle] = flwdir
        return flwdir
    
    @flwdir.setter
    def flwdir(self, flwdir):
        self.flwdir[...] = flwdir
    
    @property
    def flwacc(self):
        """
        Element flwacc ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 57
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__flwacc(self._handle)
        if array_handle in self._arrays:
            flwacc = self._arrays[array_handle]
        else:
            flwacc = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__flwacc)
            self._arrays[array_handle] = flwacc
        return flwacc
    
    @flwacc.setter
    def flwacc(self, flwacc):
        self.flwacc[...] = flwacc
    
    @property
    def flwdst(self):
        """
        Element flwdst ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 58
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__flwdst(self._handle)
        if array_handle in self._arrays:
            flwdst = self._arrays[array_handle]
        else:
            flwdst = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__flwdst)
            self._arrays[array_handle] = flwdst
        return flwdst
    
    @flwdst.setter
    def flwdst(self, flwdst):
        self.flwdst[...] = flwdst
    
    @property
    def npar(self):
        """
        Element npar ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 59
        
        """
        return _libfcore.f90wrap_meshdt__get__npar(self._handle)
    
    @npar.setter
    def npar(self, npar):
        _libfcore.f90wrap_meshdt__set__npar(self._handle, npar)
    
    @property
    def ncpar(self):
        """
        Element ncpar ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 60
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__ncpar(self._handle)
        if array_handle in self._arrays:
            ncpar = self._arrays[array_handle]
        else:
            ncpar = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__ncpar)
            self._arrays[array_handle] = ncpar
        return ncpar
    
    @ncpar.setter
    def ncpar(self, ncpar):
        self.ncpar[...] = ncpar
    
    @property
    def cscpar(self):
        """
        Element cscpar ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 61
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__cscpar(self._handle)
        if array_handle in self._arrays:
            cscpar = self._arrays[array_handle]
        else:
            cscpar = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__cscpar)
            self._arrays[array_handle] = cscpar
        return cscpar
    
    @cscpar.setter
    def cscpar(self, cscpar):
        self.cscpar[...] = cscpar
    
    @property
    @f90wrap_getter_index_array
    def cpar_to_rowcol(self):
        """
        Element cpar_to_rowcol ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 62
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__cpar_to_rowcol(self._handle)
        if array_handle in self._arrays:
            cpar_to_rowcol = self._arrays[array_handle]
        else:
            cpar_to_rowcol = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__cpar_to_rowcol)
            self._arrays[array_handle] = cpar_to_rowcol
        return cpar_to_rowcol
    
    @cpar_to_rowcol.setter
    @f90wrap_setter_index_array
    def cpar_to_rowcol(self, cpar_to_rowcol):
        self.cpar_to_rowcol[...] = cpar_to_rowcol
    
    @property
    def flwpar(self):
        """
        Element flwpar ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 63
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__flwpar(self._handle)
        if array_handle in self._arrays:
            flwpar = self._arrays[array_handle]
        else:
            flwpar = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__flwpar)
            self._arrays[array_handle] = flwpar
        return flwpar
    
    @flwpar.setter
    def flwpar(self, flwpar):
        self.flwpar[...] = flwpar
    
    @property
    def nac(self):
        """
        Element nac ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 64
        
        """
        return _libfcore.f90wrap_meshdt__get__nac(self._handle)
    
    @nac.setter
    def nac(self, nac):
        _libfcore.f90wrap_meshdt__set__nac(self._handle, nac)
    
    @property
    def active_cell(self):
        """
        Element active_cell ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 65
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__active_cell(self._handle)
        if array_handle in self._arrays:
            active_cell = self._arrays[array_handle]
        else:
            active_cell = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__active_cell)
            self._arrays[array_handle] = active_cell
        return active_cell
    
    @active_cell.setter
    def active_cell(self, active_cell):
        self.active_cell[...] = active_cell
    
    @property
    def ng(self):
        """
        Element ng ftype=integer  pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 66
        
        """
        return _libfcore.f90wrap_meshdt__get__ng(self._handle)
    
    @ng.setter
    def ng(self, ng):
        _libfcore.f90wrap_meshdt__set__ng(self._handle, ng)
    
    @property
    @f90wrap_getter_index_array
    def gauge_pos(self):
        """
        Element gauge_pos ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 67
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__gauge_pos(self._handle)
        if array_handle in self._arrays:
            gauge_pos = self._arrays[array_handle]
        else:
            gauge_pos = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__gauge_pos)
            self._arrays[array_handle] = gauge_pos
        return gauge_pos
    
    @gauge_pos.setter
    @f90wrap_setter_index_array
    def gauge_pos(self, gauge_pos):
        self.gauge_pos[...] = gauge_pos
    
    @property
    @f90wrap_getter_char_array
    def code(self):
        """
        Element code ftype=character(lchar) pytype=str
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 68
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__code(self._handle)
        if array_handle in self._arrays:
            code = self._arrays[array_handle]
        else:
            code = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__code)
            self._arrays[array_handle] = code
        return code
    
    @code.setter
    @f90wrap_setter_char_array
    def code(self, code):
        self.code[...] = code
    
    @property
    def area(self):
        """
        Element area ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 69
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__area(self._handle)
        if array_handle in self._arrays:
            area = self._arrays[array_handle]
        else:
            area = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__area)
            self._arrays[array_handle] = area
        return area
    
    @area.setter
    def area(self, area):
        self.area[...] = area
    
    @property
    def area_dln(self):
        """
        Element area_dln ftype=real(sp) pytype=float
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 70
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__area_dln(self._handle)
        if array_handle in self._arrays:
            area_dln = self._arrays[array_handle]
        else:
            area_dln = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__area_dln)
            self._arrays[array_handle] = area_dln
        return area_dln
    
    @area_dln.setter
    def area_dln(self, area_dln):
        self.area_dln[...] = area_dln
    
    @property
    @f90wrap_getter_index_array
    def rowcol_to_ind_ac(self):
        """
        Element rowcol_to_ind_ac ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 71
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__rowcol_to_ind_ac(self._handle)
        if array_handle in self._arrays:
            rowcol_to_ind_ac = self._arrays[array_handle]
        else:
            rowcol_to_ind_ac = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__rowcol_to_ind_ac)
            self._arrays[array_handle] = rowcol_to_ind_ac
        return rowcol_to_ind_ac
    
    @rowcol_to_ind_ac.setter
    @f90wrap_setter_index_array
    def rowcol_to_ind_ac(self, rowcol_to_ind_ac):
        self.rowcol_to_ind_ac[...] = rowcol_to_ind_ac
    
    @property
    def local_active_cell(self):
        """
        Element local_active_cell ftype=integer pytype=int
        
        
        Defined at ../smash/fcore/derived_type/mwd_mesh.f90 line 72
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _libfcore.f90wrap_meshdt__array__local_active_cell(self._handle)
        if array_handle in self._arrays:
            local_active_cell = self._arrays[array_handle]
        else:
            local_active_cell = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    self._handle,
                                    _libfcore.f90wrap_meshdt__array__local_active_cell)
            self._arrays[array_handle] = local_active_cell
        return local_active_cell
    
    @local_active_cell.setter
    def local_active_cell(self, local_active_cell):
        self.local_active_cell[...] = local_active_cell
    
    
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
    

def meshdt_copy(self):
    """
    this_copy = meshdt_copy(self)
    
    
    Defined at ../smash/fcore/derived_type/mwd_mesh.f90 lines 121-125
    
    Parameters
    ----------
    this : Meshdt
    
    Returns
    -------
    this_copy : Meshdt
    
    """
    this_copy = _libfcore.f90wrap_mwd_mesh__meshdt_copy(this=self._handle)
    this_copy = \
        f90wrap.runtime.lookup_class("libfcore.MeshDT").from_handle(this_copy, \
        alloc=True)
    return this_copy


_array_initialisers = []
_dt_array_initialisers = []

try:
    for func in _array_initialisers:
        func()
except ValueError:
    logging.debug('unallocated array(s) detected on import of module "mwd_mesh".')

for func in _dt_array_initialisers:
    func()

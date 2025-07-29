
cimport debug_mgr.core as dm_core
cimport vsc_solvers.decl as decl
cimport vsc_dm.core as vsc_dm
from libc.stdint cimport intptr_t
from libc.stdint cimport int32_t
from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from libc.stdint cimport int64_t
from libcpp.string cimport string as cpp_string
from libcpp.vector cimport vector as cpp_vector
from libcpp cimport bool

cdef class CompoundSolver(object):
    cdef decl.ICompoundSolver   *_hndl

    cpdef bool solve(self, RandState randstate, fields, constraints, flags)

    @staticmethod
    cdef mk(decl.ICompoundSolver *)

cdef class Factory(object):
    cdef decl.IFactory         *_hndl

    cdef init(self, dm_core.Factory f)

    cpdef RandState mkRandState(self, seed)

    cpdef CompoundSolver mkCompoundSolver(self)

cdef class RandState(object):
    cdef decl.IRandState       *_hndl

    cpdef str seed(self)

    cpdef randint32(self, int32_t, int32_t)
#    cpdef randbits(self, vsc_dm.ModelVal)

    cpdef void setState(self, RandState other)
    cpdef RandState clone(self)
    cpdef RandState next(self)

    @staticmethod
    cdef mk(decl.IRandState *)


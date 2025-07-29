

cimport debug_mgr.decl as dm_decl
cimport vsc_dm.decl as vsc_dm_decl
from libc.stdint cimport intptr_t
from libc.stdint cimport int32_t
from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from libc.stdint cimport int64_t
from libcpp.string cimport string as cpp_string
from libcpp.vector cimport vector as cpp_vector
from libcpp cimport bool

ctypedef IFactory *IFactoryP
ctypedef IRandState *IRandStateP

cdef extern from "vsc/solvers/ICompoundSolver.h" namespace "vsc::solvers":
    cdef enum SolveFlags:
        Randomize          "vsc::solvers::SolveFlags::Randomize"
        RandomizeDeclRand  "vsc::solvers::SolveFlags::RandomizeDeclRand"
        RandomizeTopFields "vsc::solvers::SolveFlags::RandomizeTopFields"
        DiagnoseFailures   "vsc::solvers::SolveFlags::DiagnoseFailures"

    cdef cppclass ICompoundSolver:
        bool solve(
            IRandState                                          *randstate,
            const cpp_vector[vsc_dm_decl.IModelFieldP]          &fields,
            const cpp_vector[vsc_dm_decl.IModelConstraintP]     &constraints,
            SolveFlags                                          flags
        )

cdef extern from "vsc/solvers/IFactory.h" namespace "vsc::solvers":
    cdef cppclass IFactory:
        void init(dm_decl.IDebugMgr *)

        dm_decl.IDebugMgr *getDebugMgr()

        ICompoundSolver *mkCompoundSolver()

        IRandState *mkRandState(const cpp_string &seed)

cdef extern from "vsc/solvers/IRandState.h" namespace "vsc::solvers":
    cdef cppclass IRandState:
        const cpp_string &seed() const
        int32_t randint32(int32_t, int32_t)
        uint64_t rand_ui64()
        int64_t rand_i64()
        void randbits(vsc_dm_decl.IModelVal *)
        void setState(IRandState *)
        IRandState *clone() const
        IRandState *next()        


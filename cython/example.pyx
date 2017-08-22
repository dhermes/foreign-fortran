import ctypes
from libc.stdint cimport intptr_t

import cython
import numpy as np
cimport numpy as np

cimport example_fortran


def foo(double bar, double baz):
    cdef double quux
    example_fortran.foo(bar, baz, &quux)
    return quux


def make_udf(double buzz, double broken, int how_many):
    cdef example_fortran.UserDefined made_it
    example_fortran.make_udf(&buzz, &broken, &how_many, &made_it)
    return made_it


@cython.boundscheck(False)
@cython.wraparound(False)
def foo_array(np.ndarray[double, ndim=2, mode='fortran'] val not None):
    cdef int size
    cdef np.ndarray[double, ndim=2, mode='fortran'] two_val

    size = np.shape(val)[0]
    two_val = np.empty_like(val)
    example_fortran.foo_array(
        &size,
        &val[0, 0],
        &two_val[0, 0],
    )
    return two_val


def udf_ptr():
    cdef example_fortran.UserDefined made_it
    cdef intptr_t ptr_as_int = <intptr_t> (&made_it)
    example_fortran.udf_ptr(&ptr_as_int)
    return made_it


def just_print():
    example_fortran.just_print()

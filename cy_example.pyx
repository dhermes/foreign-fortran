import ctypes
from libc.stdint cimport intptr_t

import cython
import numpy as np
cimport numpy as np


cdef extern:
    void foo(double bar, double baz, double *quux)
    void make_udf(double buzz, double broken, int how_many, UserDefined *made_it)
    void foo_array(int *size, double *val, double *two_val)
    void udf_ptr(intptr_t *ptr_as_int)


cdef struct UserDefined:
    double buzz
    double broken
    int how_many


def foo_(double bar, double baz):
    cdef double quux
    foo(bar, baz, &quux)
    return quux


def make_udf_(double buzz, double broken, int how_many):
    cdef UserDefined made_it
    make_udf(buzz, broken, how_many, &made_it)
    return made_it


@cython.boundscheck(False)
@cython.wraparound(False)
def foo_array_(np.ndarray[double, ndim=2, mode='fortran'] val not None):
    cdef int size
    cdef np.ndarray[double, ndim=2, mode='fortran'] two_val

    size = np.shape(val)[0]
    two_val = np.empty_like(val)
    foo_array(
        &size,
        &val[0, 0],
        &two_val[0, 0],
    )
    return two_val


def udf_ptr_():
    cdef UserDefined made_it
    cdef intptr_t ptr_as_int = <intptr_t> (&made_it)
    udf_ptr(&ptr_as_int)
    return made_it

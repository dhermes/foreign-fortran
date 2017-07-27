import ctypes

import cython
import numpy as np
cimport numpy as np


cdef extern:
    void foo(double bar, double baz, double *quux)
    void foo_array(int size, double *val, double *two_val)


def foo_(double bar, double baz):
    cdef double quux
    foo(bar, baz, &quux)
    return quux


@cython.boundscheck(False)
@cython.wraparound(False)
def foo_array_(np.ndarray[double, ndim=2, mode='fortran'] val not None):
    cdef int size
    cdef np.ndarray[double, ndim=2, mode='fortran'] two_val

    size = np.shape(val)[0]
    two_val = np.empty_like(val)
    foo_array(
        size,
        &val[0, 0],
        &two_val[0, 0],
    )
    return two_val

import numpy as np

cdef extern:
    void foo(double bar, double baz, double *quux)

def foo_cython(double bar, double baz):
    cdef double quux
    foo(bar, baz, &quux)
    return quux

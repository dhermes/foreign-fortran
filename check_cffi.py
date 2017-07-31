from __future__ import print_function

import os

import cffi  # 1.10.0
import numpy as np  # 1.13.1

from check_ctypes import FOO_ARRAY_TEMPLATE
from check_ctypes import SEPARATOR


HERE = os.path.abspath(os.path.dirname(__file__))
SO_FILE = os.path.join(HERE, 'example.so')
STRUCT_CDEF = """\
struct UserDefined {
  double buzz;
  double broken;
  int how_many;
};
"""
MAKE_UDF_DEF = """\
void make_udf(double buzz, double broken,
              int how_many, struct UserDefined *quux);
"""
MAKE_UDF_TEMPLATE = """\
quuz = make_udf({0}, {1}, {2})
     = UserDefined({3.buzz}, {3.broken}, {3.how_many})
"""


def numpy_pointer(array, ffi):
    assert array.dtype == np.float64
    return ffi.cast('double *', array.ctypes.data)


def main():
    ffi = cffi.FFI()
    ffi.cdef('void foo(double bar, double baz, double *quux);')
    ffi.cdef(STRUCT_CDEF)
    ffi.cdef(MAKE_UDF_DEF)
    ffi.cdef('void foo_array(int *size, double *val, double *two_val);')
    lib_example = ffi.dlopen(SO_FILE)

    print(SEPARATOR)
    # foo()
    bar = 1.0
    baz = 16.0
    quux_ptr = ffi.new('double *')
    lib_example.foo(bar, baz, quux_ptr)
    quux = quux_ptr[0]
    print('quux = foo({}, {}) = {}'.format(bar, baz, quux))

    print(SEPARATOR)
    # make_udf()
    buzz = 1.25
    broken = 5.0
    how_many = 1337
    quuz_ptr = ffi.new('struct UserDefined *')
    lib_example.make_udf(buzz, broken, how_many, quuz_ptr)
    quuz = quuz_ptr[0]
    msg = MAKE_UDF_TEMPLATE.format(buzz, broken, how_many, quuz)
    print(msg, end='')

    print(SEPARATOR)
    # foo_array()
    val = np.asfortranarray([
        [ 3.0, 4.5 ],
        [ 1.0, 1.25],
        [ 9.0, 0.0 ],
        [-1.0, 4.0 ],
    ])
    shape = val.shape
    two_val = np.empty(shape, order='F')
    size_ptr = ffi.new('int *')
    size_ptr[0], _ = shape

    lib_example.foo_array(
        size_ptr,
        numpy_pointer(val, ffi),
        numpy_pointer(two_val, ffi),
    )
    msg = FOO_ARRAY_TEMPLATE.format(val, size_ptr[0], two_val)
    print(msg, end='')


if __name__ == '__main__':
    main()

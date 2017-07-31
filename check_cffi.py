import os

import cffi  # 1.10.0

from check_ctypes import SEPARATOR


HERE = os.path.abspath(os.path.dirname(__file__))
SO_FILE = os.path.join(HERE, 'example.so')


def main():
    ffi = cffi.FFI()
    ffi.cdef('void foo(double bar, double baz, double *quux);')
    lib_example = ffi.dlopen(SO_FILE)

    print(SEPARATOR)
    # foo()
    bar = 1.0
    baz = 16.0
    quux_ptr = ffi.new('double *')
    lib_example.foo(bar, baz, quux_ptr)
    quux = quux_ptr[0]
    print('quux = foo({}, {}) = {}'.format(bar, baz, quux))


if __name__ == '__main__':
    main()

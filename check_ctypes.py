import ctypes
import os
import struct

import cffi  # 1.10.0
import numpy as np  # 1.13.1


HERE = os.path.abspath(os.path.dirname(__file__))
SO_FILE = os.path.join(HERE, 'example.so')
SEPARATOR = '-' * 60


class UserDefined(ctypes.Structure):
    _fields_ = [
        ('buzz', ctypes.c_double),
        ('broken', ctypes.c_double),
        ('how_many', ctypes.c_int),
    ]

    def __repr__(self):
        template = (
            'UserDefined(buzz={self.buzz}, broken={self.broken}, '
            'how_many={self.how_many})')
        return template.format(self=self)


def numpy_pointer(array):
    return array.ctypes.data_as(ctypes.POINTER(ctypes.c_double))


def verify_pointer_size():
    ffi = cffi.FFI()
    assert ffi.sizeof('intptr_t') == ffi.sizeof('long')


def prepare_udf():
    made_it = UserDefined()
    raw_pointer = ctypes.cast(
        ctypes.pointer(made_it), ctypes.c_void_p)
    # Make sure it's "OK" to use a ``long`` here.
    verify_pointer_size()
    ptr_as_int = ctypes.c_long(raw_pointer.value)
    return made_it, ptr_as_int


def main():
    lib_example = ctypes.cdll.LoadLibrary(SO_FILE)
    print(lib_example)

    # foo()
    bar = ctypes.c_double(1.0)
    baz = ctypes.c_double(16.0)
    quux = ctypes.c_double()
    lib_example.foo(bar, baz, ctypes.byref(quux))
    print('quux = foo({}, {}) = {}'.format(bar, baz, quux))

    print(SEPARATOR)
    # make_udf()
    buzz = ctypes.c_double(1.25)
    broken = ctypes.c_double(5.0)
    how_many = ctypes.c_int(1337)
    quuz = UserDefined()
    lib_example.make_udf(buzz, broken, how_many, ctypes.byref(quuz))
    msg = 'quuz = make_udf({}, {}, {}) = {}'.format(
        buzz, broken, how_many, quuz)
    print(msg)
    print('quuz needsfree: {}'.format(bool(quuz._b_needsfree_)))
    quuz_address = ctypes.addressof(quuz)
    print('address(quuz) = {}'.format(quuz_address))
    alt_quuz = UserDefined.from_address(quuz_address)
    print('*address(quuz) = {}'.format(alt_quuz))

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
    size, _ = shape

    size = ctypes.c_int(size)
    lib_example.foo_array(
        ctypes.byref(size),
        numpy_pointer(val),
        numpy_pointer(two_val),
    )
    print('val =\n{}'.format(val))
    print('two_val = foo_array({}, val)'.format(size))
    print('two_val =\n{}'.format(two_val))

    print(SEPARATOR)
    # udf_ptr()
    made_it, ptr_as_int = prepare_udf()
    print('ptr_as_int: {}'.format(ptr_as_int))
    lib_example.udf_ptr(ctypes.byref(ptr_as_int))

    print('made_it: {}'.format(made_it))
    print('made_it needsfree: {}'.format(bool(made_it._b_needsfree_)))
    alt_made_it = UserDefined.from_address(ptr_as_int.value)
    print('*address = {}'.format(alt_made_it))


if __name__ == '__main__':
    main()

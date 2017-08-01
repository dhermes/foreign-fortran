from __future__ import print_function

import ctypes
import os

import cffi  # 1.10.0
import numpy as np  # 1.13.1


HERE = os.path.abspath(os.path.dirname(__file__))
SO_FILE = os.path.join(HERE, 'example.so')
SEPARATOR = '-' * 60
UDF_PTR_TEMPLATE = """\
ptr_as_int = address(made_it)  # intptr_t / ssize_t / long
ptr_as_int = {}  # 0x{:x}
udf_ptr(ptr_as_int)  # Set memory in ``made_it``
made_it = {}
"""
FOO_ARRAY_TEMPLATE = """\
val =
{}
two_val = foo_array({}, val)
two_val =
{}
"""


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


class DataContainer(ctypes.Structure):
    _fields_ = [
        ('data', ctypes.POINTER(ctypes.c_double)),
    ]

    @property
    def data_array(self):
        return np.ctypeslib.as_array(self.data, shape=(2, 4)).T


def numpy_pointer(array):
    return array.ctypes.data_as(ctypes.POINTER(ctypes.c_double))


def verify_pointer_size():
    ffi = cffi.FFI()
    assert ffi.sizeof('intptr_t') == ffi.sizeof('ssize_t')
    # NOTE: On many platforms, ``ctypes.c_ssize_t is ctypes.c_long``.
    return ctypes.c_ssize_t


def prepare_udf():
    made_it = UserDefined()
    raw_pointer = ctypes.cast(
        ctypes.pointer(made_it), ctypes.c_void_p)
    # Make sure it's "OK" to use a ``long`` here.
    ptr_type = verify_pointer_size()
    ptr_as_int = ptr_type(raw_pointer.value)
    return made_it, ptr_as_int


def main():
    print(SEPARATOR)
    lib_example = ctypes.cdll.LoadLibrary(SO_FILE)
    print(lib_example)

    print(SEPARATOR)
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
    msg = 'quuz = make_udf({}, {}, {})\n     = {}'.format(
        buzz, broken, how_many, quuz)
    print(msg)
    print('needsfree(quuz) = {}'.format(bool(quuz._b_needsfree_)))
    quuz_address = ctypes.addressof(quuz)
    print('address(quuz) = {0}  # 0x{0:x}'.format(quuz_address))
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
    msg = FOO_ARRAY_TEMPLATE.format(val, size, two_val)
    print(msg, end='')

    print(SEPARATOR)
    # udf_ptr()
    made_it, ptr_as_int = prepare_udf()
    lib_example.udf_ptr(ctypes.byref(ptr_as_int))
    msg = UDF_PTR_TEMPLATE.format(ptr_as_int, ptr_as_int.value, made_it)
    print(msg, end='')
    print('needsfree(made_it) = {}'.format(bool(made_it._b_needsfree_)))
    alt_made_it = UserDefined.from_address(ptr_as_int.value)
    print('*ptr_as_int = {}'.format(alt_made_it))

    print(SEPARATOR)
    # make_container()
    contained = np.asfortranarray([
        [0.0, 4.0],
        [1.0, 9.0],
        [1.0, 2.0],
        [3.0, 1.0],
    ])
    container = DataContainer()
    lib_example.make_container(
        numpy_pointer(contained),
        ctypes.byref(container),
    )
    print('contained =\n{}'.format(contained))
    print('address(contained) = {0}  # 0x{0:x}'.format(contained.ctypes.data))
    print('container = make_container(contained)')
    print('container.data =\n{}'.format(container.data_array))
    addr = ctypes.cast(container.data, ctypes.c_void_p)
    print('address(container.data) = {0}  # 0x{0:x}'.format(addr.value))

    print(SEPARATOR)
    # just_print()
    print('just_print()')
    lib_example.just_print()


if __name__ == '__main__':
    main()

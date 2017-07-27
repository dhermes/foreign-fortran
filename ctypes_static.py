import ctypes
import os

import numpy as np


HERE = os.path.abspath(os.path.dirname(__file__))
SO_FILE = os.path.join(HERE, 'example.so')



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


def main():
    lib_example = ctypes.cdll.LoadLibrary(SO_FILE)
    print(lib_example)

    bar = ctypes.c_double(1.0)
    baz = ctypes.c_double(16.0)
    quux = ctypes.c_double()
    lib_example.foo(bar, baz, ctypes.pointer(quux))
    print('quux = foo({}, {}) = {}'.format(bar, baz, quux))

    buzz = ctypes.c_double(1.25)
    broken = ctypes.c_double(5.0)
    how_many = ctypes.c_int(1337)
    quuz = UserDefined()
    lib_example.make_udf(buzz, broken, how_many, ctypes.pointer(quuz))
    msg = 'quuz = make_udf({}, {}, {}) = {}'.format(
        buzz, broken, how_many, quuz)
    print(msg)

    val = np.asfortranarray([
        [ 3.0, 4.5 ],
        [ 1.0, 1.25],
        [ 9.0, 0.0 ],
        [-1.0, 4.0 ],
    ])
    size, _ = val.shape
    two_val = np.empty((size, 2), order='F')
    lib_example.foo_array(
        ctypes.c_int(size),
        numpy_pointer(val),
        numpy_pointer(two_val),
    )
    print('val =\n{}'.format(val))
    print('two_val = foo_array({}, val)'.format(size))
    print('two_val =\n{}'.format(two_val))


if __name__ == '__main__':
    main()

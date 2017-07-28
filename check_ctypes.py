import ctypes
import os
import struct

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


UserDefined_ptr = ctypes.POINTER(UserDefined)


def numpy_pointer(array):
    return array.ctypes.data_as(ctypes.POINTER(ctypes.c_double))


def main():
    lib_example = ctypes.cdll.LoadLibrary(SO_FILE)
    print(lib_example)

    # udf_ptr()
    made_it_ptr = UserDefined_ptr()
    lib_example.udf_ptr(ctypes.byref(made_it_ptr))
    print('made_it_ptr: {}'.format(made_it_ptr))
    raw_pointer = ctypes.cast(made_it_ptr, ctypes.c_void_p)
    print('address: {}'.format(raw_pointer.value))

    made_it = made_it_ptr[0]
    print('made_it: {}'.format(made_it))
    alt_made_it = UserDefined.from_address(raw_pointer.value)
    print('*address = {}'.format(alt_made_it))


if __name__ == '__main__':
    main()

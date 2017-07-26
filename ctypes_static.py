import ctypes
import os


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


if __name__ == '__main__':
    main()

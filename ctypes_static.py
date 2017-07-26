import ctypes
import os


HERE = os.path.abspath(os.path.dirname(__file__))
SO_FILE = os.path.join(HERE, 'example.so')


def main():
    lib_example = ctypes.cdll.LoadLibrary(SO_FILE)
    print(lib_example)

    bar = ctypes.c_double(1.0)
    baz = ctypes.c_double(16.0)
    quux = ctypes.c_double()
    lib_example.foo(bar, baz, ctypes.pointer(quux))
    print('bar = {}'.format(bar))
    print('baz = {}'.format(baz))
    print('quux = {}'.format(quux))


if __name__ == '__main__':
    main()

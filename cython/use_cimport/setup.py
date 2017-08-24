import os
import sys

import Cython.Build
import setuptools

import example


MAC_OS_X = 'darwin'


def main():
    example_include = example.get_include()
    example_lib = example.get_lib()

    extra_link_args = None
    if sys.platform == MAC_OS_X:
        linker_args = ('-Wl', '-rpath', example_lib)
        extra_link_args = (','.join(linker_args),)

    ext_module = setuptools.Extension(
        'wrapper',
        ['wrapper.pyx'],
        include_dirs=[example_include],
        libraries=['example'],
        library_dirs=[example_lib],
        runtime_library_dirs=[example_lib],
        extra_link_args=extra_link_args,
    )
    setuptools.setup(
        name='cimport-ing example module interface',
        ext_modules=Cython.Build.cythonize([ext_module]),
    )


if __name__ == '__main__':
    main()

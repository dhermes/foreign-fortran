import distutils.core
import distutils.extension

import Cython.Build

import example


def main():
    example_include = example.get_include()
    example_lib = example.get_lib()

    ext_module = distutils.extension.Extension(
        'wrapper',
        ['wrapper.pyx'],
        include_dirs=[example_include],
        libraries=['example'],
        library_dirs=[example_lib],
        runtime_library_dirs=[example_lib],
    )
    distutils.core.setup(
        name='cimport-ing example module interface',
        ext_modules=Cython.Build.cythonize([ext_module]),
    )


if __name__ == '__main__':
    main()

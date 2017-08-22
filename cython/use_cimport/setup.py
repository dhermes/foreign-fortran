import distutils.core

import Cython.Build

import example


def main():
    ext_modules = Cython.Build.cythonize('wrapper.pyx')
    example_include = example.get_include()
    distutils.core.setup(
        name='cimport-ing example module interface',
        ext_modules=ext_modules,
        include_dirs=[example_include],
    )


if __name__ == '__main__':
    main()

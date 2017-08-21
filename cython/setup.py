# NOTE: This is **ONLY** for Cython.
import distutils.core
import distutils.extension
import Cython.Distutils
import numpy


def main():
    npy_include_dir = numpy.get_include()
    ext_modules = [
        distutils.extension.Extension(
            'cy_example',
            ['cy_example.pyx'],
            include_dirs=[npy_include_dir],
            libraries=['gfortran'],
            extra_objects=[
                'example.o',
            ],
        ),
    ]
    distutils.core.setup(
        name='Cython Example calling Fortran',
        cmdclass={'build_ext': Cython.Distutils.build_ext},
        ext_modules=ext_modules,
   )


if __name__ == '__main__':
    main()

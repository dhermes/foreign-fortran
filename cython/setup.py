import distutils.core
import distutils.extension
import os

import Cython.Distutils
import numpy as np


if 'IGNORE_LIBRARIES' in os.environ:
    LIBRARIES = []
else:
    LIBRARIES = ['gfortran']


def main():
    npy_include_dir = np.get_include()
    ext_modules = [
        distutils.extension.Extension(
            'example',
            ['example.pyx'],
            include_dirs=[npy_include_dir],
            libraries=LIBRARIES,
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

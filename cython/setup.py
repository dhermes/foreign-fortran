import distutils.ccompiler
import distutils.core
import distutils.extension
import os

import Cython.Distutils
import numpy.distutils.core
import numpy.distutils.fcompiler
import numpy as np


def get_f90_compiler():
    c_compiler = distutils.ccompiler.new_compiler()
    c_compiler.verbose = 2

    f90_compiler = numpy.distutils.fcompiler.new_fcompiler(
        requiref90=True, c_compiler=c_compiler)
    dist = numpy.distutils.core.get_distribution(always=True)
    f90_compiler.customize(dist)
    f90_compiler.verbose = 2

    return f90_compiler


def compile_fortran():
    # NOTE: We prefer the relative path below over the absolute path
    #           source_file = os.path.abspath(os.path.join(
    #               os.path.dirname(__file__),
    #               'example.f90',
    #           ))
    #       because ``compile()`` will create the entire subdirectory
    #       path matching it.
    source_file = 'example.f90'
    f90_compiler = get_f90_compiler()
    obj_file, = f90_compiler.compile(
        [source_file],
        output_dir=None,
        macros=[],
        include_dirs=[],
        debug=None,
        extra_postargs=[],
        depends=[],
    )

    libraries = []
    if 'IGNORE_LIBRARIES' not in os.environ:
        libraries.extend(f90_compiler.libraries)

    return obj_file, libraries


def main():
    obj_file, libraries = compile_fortran()
    npy_include_dir = np.get_include()
    ext_modules = [
        distutils.extension.Extension(
            'example',
            ['example.pyx'],
            include_dirs=[npy_include_dir],
            libraries=libraries,
            extra_objects=[
                obj_file,
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

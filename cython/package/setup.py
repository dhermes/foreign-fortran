import distutils.ccompiler
import distutils.core
import distutils.extension
import os

import numpy.distutils.core
import numpy.distutils.fcompiler
import numpy as np


VERSION = '0.0.1'
LOCAL_INCLUDE = os.path.join('example', 'include')
LOCAL_LIB = os.path.join('example', '.lib')
# NOTE: We prefer the relative path below over the absolute path
#           source_file = os.path.abspath(os.path.join(
#               os.path.dirname(__file__),
#               'example.f90',
#           ))
#       because ``compile()`` will create the entire subdirectory
#       path matching it.
SOURCE_FILE = os.path.join('example', 'example.f90')


def get_f90_compiler():
    c_compiler = distutils.ccompiler.new_compiler()
    c_compiler.verbose = 2

    f90_compiler = numpy.distutils.fcompiler.new_fcompiler(
        requiref90=True, c_compiler=c_compiler)
    dist = numpy.distutils.core.get_distribution(always=True)
    f90_compiler.customize(dist)
    f90_compiler.verbose = 2

    return f90_compiler


def compile_fortran_obj_file(f90_compiler):
    obj_file, = f90_compiler.compile(
        [SOURCE_FILE],
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


def compile_fortran_so_file(f90_compiler, obj_file):
    objects = [obj_file]
    # NOTE: It's unclear why we need to specify 'libexample' rather than
    #       'example'. I.e. I expect the tooling to add `lib` when appropriate
    #       based on the `shared_lib` in the name.
    output_libname = 'libexample'
    f90_compiler.link_shared_lib(
        objects,
        output_libname,
        output_dir=LOCAL_LIB,
    )


def main():
    f90_compiler = get_f90_compiler()
    obj_file, libraries = compile_fortran_obj_file(f90_compiler)
    compile_fortran_so_file(f90_compiler, obj_file)

    npy_include_dir = np.get_include()
    cython_extension = distutils.extension.Extension(
        'example.fast',
        [os.path.join('example', 'fast.c')],
        include_dirs=[
            npy_include_dir,
            LOCAL_INCLUDE,
        ],
        libraries=libraries,
        extra_objects=[
            obj_file,
        ],
    )
    distutils.core.setup(
        name='example',
        version=VERSION,
        description='Cython Example calling Fortran',
        author='Danny Hermes',
        author_email='daniel.j.hermes@gmail.com',
        url='https://github.com/dhermes/foreign-fortran',
        packages=['example'],
        ext_modules=[cython_extension],
        package_data = {
            'example': [
                'example_fortran.pxd',
                os.path.join('include', '*.h'),
                os.path.join('.lib', '*.so'),
            ],
        },
    )


if __name__ == '__main__':
    main()

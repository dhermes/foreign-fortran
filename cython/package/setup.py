from __future__ import print_function
from __future__ import unicode_literals

import distutils.ccompiler
import distutils.core
import distutils.extension
import glob
import os
import subprocess
import sys

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
FORTRAN_LIBRARY_PREFIX = 'libraries: ='
ERR_MSG = 'Fortran search default library path not found.'
BAD_PATH = 'Path {} is not a directory.'
MAC_OS_X = 'darwin'


def fortran_executable(f90_compiler):
    version_cmd = f90_compiler.version_cmd
    if len(version_cmd) != 2 or version_cmd[1] != '-dumpversion':
        raise ValueError(
            'Unexpected Fortran version command',
            version_cmd)

    return version_cmd[0]


def fortran_search_path(f90_compiler):
    cmd = (
        fortran_executable(f90_compiler),
        '-print-search-dirs',
    )
    cmd_output = subprocess.check_output(cmd).decode('utf-8')

    search_lines = cmd_output.strip().split('\n')
    library_lines = [
        line[len(FORTRAN_LIBRARY_PREFIX):]
        for line in search_lines
        if line.startswith(FORTRAN_LIBRARY_PREFIX)
    ]
    if len(library_lines) != 1:
        print(ERR_MSG, file=sys.stderr)
        sys.exit(1)

    library_line = library_lines[0]
    accepted = set(f90_compiler.library_dirs)
    for part in library_line.split(':'):
        full_path = os.path.abspath(part)

        if not os.path.exists(full_path):
            continue

        if not os.path.isdir(full_path):
            msg = BAD_PATH.format(full_path)
            print(msg, file=sys.stderr)
            sys.exit(1)

        accepted.add(full_path)

    return tuple(accepted)


def get_library_dirs(f90_compiler):
    if sys.platform == MAC_OS_X:
        return fortran_search_path(f90_compiler)
    else:
        return f90_compiler.library_dirs


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
    library_dirs = []
    if 'IGNORE_LIBRARIES' not in os.environ:
        libraries.extend(f90_compiler.libraries)
        library_dirs.extend(get_library_dirs(f90_compiler))

    return obj_file, libraries, library_dirs


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


def add_by_glob(pattern, example_files, prefix):
    for filename in glob.glob(pattern, recursive=True):
        if os.path.isdir(filename):
            continue

        # NOTE: We assume but don't check that `_` is the empty
        #       string (i.e. `filename` starts with the prefix.
        _, relative_name = filename.split(prefix, 1)
        example_files.append(relative_name)


def get_package_data():
    example_files = [
        'example_fortran.pxd',
    ]

    prefix = 'example' + os.path.sep

    include_glob = os.path.join(LOCAL_INCLUDE, '*.h')
    add_by_glob(include_glob, example_files, prefix)

    lib_glob = os.path.join(LOCAL_LIB, '**')
    add_by_glob(lib_glob, example_files, prefix)

    return {'example': example_files}


def main():
    f90_compiler = get_f90_compiler()
    obj_file, libraries, library_dirs = compile_fortran_obj_file(f90_compiler)
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
        library_dirs=library_dirs,
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
        package_data=get_package_data(),
    )


if __name__ == '__main__':
    main()

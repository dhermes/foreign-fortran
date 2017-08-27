from __future__ import print_function

import distutils.ccompiler
import os
import subprocess
import sys

import numpy.distutils.ccompiler
import numpy.distutils.core
import numpy.distutils.fcompiler
import numpy as np
import setuptools


VERSION = '0.0.1'
LOCAL_INCLUDE = os.path.join('example', 'include')
LOCAL_LIB = os.path.join('example', 'lib')
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
MAC_OS_LINKER_ERR = 'Unexpected `linker_so` on OS X: {}.'
MAC_OS_BUNDLE = '-bundle'
MAC_OS_DYLIB = '-dynamiclib'
JOURNAL_TEMPLATE = 'journal-{}-{}.{}.txt'
JOURNAL_SEPARATOR = '-' * 40
_CONTINUATION = ' \\\n'


def journaling_hack():
    """Capture calls to the system by compilers.

    See: https://github.com/numpy/numpy/blob/v1.13.1/\
    numpy/distutils/ccompiler.py#L154

    Returns:
        list: A list (i.e. mutable) that will be updated as
        ``spawn`` is called.
    """
    cmds = []

    def journaled_spawn(self, cmd, display=None):
        cmds.append(cmd)
        return numpy.distutils.ccompiler.CCompiler_spawn(
            self, cmd, display=None)

    numpy.distutils.ccompiler.replace_method(
        distutils.ccompiler.CCompiler,
        'spawn',
        journaled_spawn,
    )

    return cmds


def save_journal(cmds):
    """Save a "journal" of captured commands.

    This is a **really** nasty hack that relies on this `setup.py`
    file installing into a "known" virtual environment.

    Does this by inspecting the last entry in `sys.argv` and looking
    for the sub-path ``/cython/venv/include/`` as a sign for where
    the "parent" directory is.

    Args:
        cmds (List[List[str]]): A list of commands.
    """
    if not sys.argv:
        return

    final_arg = sys.argv[-1]
    # Nasty hack:
    sub_path = '{0}cython{0}venv{0}include{0}'.format(os.path.sep)
    index = final_arg.find(sub_path)
    if index == -1:
        return

    root_dir = final_arg[:index]
    filename = JOURNAL_TEMPLATE.format(
        sys.platform,
        sys.version_info[0],
        sys.version_info[1],
    )
    path = os.path.join(root_dir, 'cython', filename)

    # Dump the commands to text with nice line continuations
    # and a visual separator between each command.
    journal_parts = []
    journal_parts.append(JOURNAL_SEPARATOR + '\n')
    for cmd in cmds:
        if len(cmd) < 2:
            raise RuntimeError(
                'command had less than two arguments', cmd)
        # First argument doesn't need an indent.
        journal_parts.append(cmd[0] + _CONTINUATION)
        for arg in cmd[1:-1]:
            journal_parts.append('  ' + arg + _CONTINUATION)
        # Last argument doesn't need a continuation.
        journal_parts.append('  ' + cmd[-1] + '\n')

        journal_parts.append(JOURNAL_SEPARATOR + '\n')

    journal_content = ''.join(journal_parts)

    # Replace the "sensitive" parts of the file.
    journal_content = journal_content.replace(
        root_dir, '${foreign-fortran}')
    home_dir = os.path.expanduser('~')
    journal_content = journal_content.replace(home_dir, '${HOME}')

    # Write the journal to file.
    with open(path, 'w') as file_obj:
        file_obj.write(journal_content)


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

    return sorted(accepted)


def patch_library_dirs(f90_compiler):
    if sys.platform != MAC_OS_X:
        return

    library_dirs = f90_compiler.library_dirs
    # Update in place.
    library_dirs[:] = fortran_search_path(f90_compiler)


def get_library_dirs(f90_compiler):
    # NOTE: This is a hack to show failure when `libgfortran`
    #       is not included. (Only for the `Makefile`, not for
    #       actaul usage.)
    if 'IGNORE_LIBRARIES' in os.environ:
        return [], []
    else:
        return f90_compiler.libraries, f90_compiler.library_dirs


def get_f90_compiler():
    c_compiler = distutils.ccompiler.new_compiler()
    c_compiler.verbose = 2

    f90_compiler = numpy.distutils.fcompiler.new_fcompiler(
        requiref90=True, c_compiler=c_compiler)
    dist = numpy.distutils.core.get_distribution(always=True)
    f90_compiler.customize(dist)
    f90_compiler.verbose = 2

    patch_library_dirs(f90_compiler)

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

    return obj_file


def make_fortran_lib(f90_compiler, obj_file):
    c_compiler = f90_compiler.c_compiler
    c_compiler.create_static_lib(
        [obj_file], 'example', output_dir=LOCAL_LIB)


def add_directory(dir_name, example_files, prefix):
    for subdirectory, _, filenames in os.walk(dir_name):
        for filename in filenames:
            path = os.path.join(subdirectory, filename)
            # NOTE: We assume but don't check that `_` is the empty
            #       string (i.e. `filename` starts with the prefix.
            _, relative_name = path.split(prefix, 1)
            example_files.append(relative_name)


def get_package_data():
    example_files = ['example_fortran.pxd']

    prefix = 'example' + os.path.sep
    add_directory(LOCAL_INCLUDE, example_files, prefix)
    add_directory(LOCAL_LIB, example_files, prefix)

    return {'example': example_files}


def main():
    cmds = journaling_hack()

    f90_compiler = get_f90_compiler()
    obj_file = compile_fortran_obj_file(f90_compiler)
    make_fortran_lib(f90_compiler, obj_file)

    libraries, library_dirs = get_library_dirs(f90_compiler)
    npy_include_dir = np.get_include()
    cython_extension = setuptools.Extension(
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
    setuptools.setup(
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

    save_journal(cmds)


if __name__ == '__main__':
    main()

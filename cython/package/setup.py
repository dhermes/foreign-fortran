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
from setuptools.command import build_ext


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
JOURNAL_ENV = 'EXAMPLE_JOURNAL'


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
    return {
        'example': [
            '*.pxd',
            os.path.join('include', '*.h'),
            os.path.join('lib', '*.a'),
            os.path.join('lib', '*.lib'),
        ],
    }


class BuildFortranThenExt(build_ext.build_ext):

    # Will be set at runtime, not import time.
    F90_COMPILER = None

    def __init__(self, *args, **kwargs):
        build_ext.build_ext.__init__(self, *args, **kwargs)
        self.root_dir = self.get_root_dir()
        # NOTE: ``get_journal_file()`` depends on ``root_dir`` being set.
        self.journal_file = self.get_journal_file()
        self.commands = []

    @classmethod
    def set_compiler(cls):
        if cls.F90_COMPILER is None:
            cls.F90_COMPILER = get_f90_compiler()

    @classmethod
    def get_library_dirs(cls):
        cls.set_compiler()

        # NOTE: This is a hack to show failure when `libgfortran`
        #       is not included. (Only for the `Makefile`, not for
        #       actual usage.)
        if 'IGNORE_LIBRARIES' in os.environ:
            return [], []
        else:
            return cls.F90_COMPILER.libraries, cls.F90_COMPILER.library_dirs

    @staticmethod
    def get_root_dir():
        """Get directory where ``setup.py`` was invoked.

        This is a **really** nasty hack that relies on this ``setup.py``
        file installing into a "known" virtual environment.

        Does this by inspecting the last entry in ``sys.argv`` and looking
        for the sub-path ``/cython/venv/include/`` as a sign for where
        the "parent" directory is.

        Returns:
            Optional[str]: The root directory, if it can be
            determined.
        """
        if not sys.argv:
            return None

        final_arg = sys.argv[-1]
        # Nasty hack:
        sub_path = '{0}cython{0}venv{0}include{0}'.format(os.path.sep)
        index = final_arg.find(sub_path)
        if index == -1:
            return None

        return final_arg[:index]

    def get_journal_file(self):
        if self.root_dir is None:
            return None

        journal = os.environ.get(JOURNAL_ENV)

        if journal is None:
            filename = JOURNAL_TEMPLATE.format(
                sys.platform,
                sys.version_info[0],
                sys.version_info[1],
            )
            journal = os.path.join(self.root_dir, 'cython', filename)

        return journal

    def start_journaling(self):
        """Capture calls to the system by compilers.

        See: https://github.com/numpy/numpy/blob/v1.13.1/\
        numpy/distutils/ccompiler.py#L154

        Intercepts all calls to ``CCompiler.spawn`` and keeps the
        arguments around to be stored in the local ``commands``
        instance attribute.
        """
        if self.journal_file is None:
            return

        def journaled_spawn(patched_self, cmd, display=None):
            self.commands.append(cmd)
            return numpy.distutils.ccompiler.CCompiler_spawn(
                patched_self, cmd, display=None)

        numpy.distutils.ccompiler.replace_method(
            distutils.ccompiler.CCompiler,
            'spawn',
            journaled_spawn,
        )

    @staticmethod
    def _command_to_text(command):
        # NOTE: This assumes, but doesn't check that the command has 3
        #       or more arguments.
        first_line = '{} \\'
        middle_line = '  {} \\'
        last_line = '  {}'

        parts = [first_line.format(command[0])]
        for argument in command[1:-1]:
            parts.append(middle_line.format(argument))
        parts.append(last_line.format(command[-1]))

        return '\n'.join(parts)

    def _commands_to_text(self):
        separator = '-' * 40

        parts = [separator]
        for command in self.commands:
            command_text = self._command_to_text(command)
            parts.extend([command_text, separator])

        parts.append('')  # Trailing newline in file.
        return '\n'.join(parts)

    def save_journal(self):
        """Save journaled commands to file.

        If there is no active journal, does nothing.
        """
        if self.journal_file is None:
            return

        as_text = self._commands_to_text()
        # Replace the "sensitive" parts of the file.
        as_text = as_text.replace(
            self.root_dir, '${foreign-fortran}')
        home_dir = os.path.expanduser('~')
        as_text = as_text.replace(home_dir, '${HOME}')

        with open(self.journal_file, 'w') as file_obj:
            file_obj.write(as_text)

    def run(self):
        self.set_compiler()
        self.start_journaling()

        obj_file = compile_fortran_obj_file(self.F90_COMPILER)
        make_fortran_lib(self.F90_COMPILER, obj_file)
        # Copy into the ``build_lib`` directory (which is what will end
        # up being installed).
        lib_dir = os.path.join(self.build_lib, LOCAL_LIB)
        self.copy_tree(LOCAL_LIB, lib_dir)

        result = build_ext.build_ext.run(self)
        self.save_journal()
        return result


def main():
    libraries, library_dirs = BuildFortranThenExt.get_library_dirs()
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
            os.path.join('example', 'example.o'),
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
        cmdclass={'build_ext': BuildFortranThenExt},
    )


if __name__ == '__main__':
    main()

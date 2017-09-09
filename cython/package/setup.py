from __future__ import print_function

import distutils.ccompiler
import os
import shutil
import subprocess
import sys
import tempfile

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
    """Patch up ``f90_compiler.library_dirs``.

    This is needed on Mac OS X for a Homebrew installed ``gfortran``, which
    doesn't come with the correct library directories by default (this is
    likely unintentional).

    The ``library_dirs`` directory can be over-ridden by using the
    ``GFORTRAN_LIB`` environment variable. This might be desirable, since the
    Homebrew ``libgfortran`` is **also** not a universal binary. So this
    over-ride could be used to point to a custom made ``libgfortran.dylib``
    that is a combined version of the ``i386`` and ``x86_64`` versions of
    ``libgfortran`` provided by Homebrew.

    Args:
        f90_compiler (numpy.distutils.fcompiler.FCompiler): A Fortran compiler
            instance.
    """
    from numpy.distutils.fcompiler import gnu

    # Only Mac OS X.
    if sys.platform != MAC_OS_X:
        return
    # Only ``gfortran``.
    if not isinstance(f90_compiler, gnu.Gnu95FCompiler):
        return

    gfortran_lib = os.environ.get('GFORTRAN_LIB')
    library_dirs = f90_compiler.library_dirs

    # Update in place.
    if gfortran_lib is None:
        library_dirs[:] = fortran_search_path(f90_compiler)
    else:
        library_dirs[:] = [gfortran_lib]


def check_dual_architecture():
    """Checks if the current Python binary is dual architecture.

    Only relevant on OS X. This uses ``lipo -info`` to check that the
    executable is a "fat file" with both ``i386`` and ``x86_64``
    architectures.

    We use ``lipo -info`` rather than ``file`` because ``lipo`` is
    purpose-built for checking the architecture(s) in a file.

    This property could also be checked by looking for the presence of
    multiple architectures in
    ``distutils.sysconfig.get_config_var('LDFLAGS')``.

    Returns:
        bool: Indicating if the Python binary is dual architecture
        (:data:`True`) or single architecture (:data:`False`).
    """
    if sys.platform != MAC_OS_X:
        return False

    cmd = ('lipo', '-info', sys.executable)
    cmd_output = subprocess.check_output(cmd).decode('utf-8').strip()

    prefix = 'Architectures in the fat file: {} are: '.format(sys.executable)

    if cmd_output.startswith(prefix):
        architectures = cmd_output[len(prefix):].split()
        return 'i386' in architectures and 'x86_64' in architectures
    else:
        return False


def gfortran_supports_dual_architecture():
    """Simple check if ``gfortran`` supports dual architecture.

    Only relevant on OS X. By default, the Homebrew ``gfortran`` **does not**
    support building dual architecture object files. This checks support
    for this feature by trying to build a very simple Fortran 90 program.
    """
    if sys.platform != MAC_OS_X:
        return False

    temporary_directory = tempfile.mkdtemp(suffix='-fortran')
    source_name = os.path.join(temporary_directory, 'bar.f90')
    with open(source_name, 'w') as file_obj:
        file_obj.writelines([
            'subroutine bar(x, y)\n',
            '  integer, intent(in) :: x\n',
            '  integer, intent(out) :: y\n',
            '\n',
            '  y = x + 2\n',
            '\n',
            'end subroutine bar\n',
            '\n',
        ])

    object_name = os.path.join(temporary_directory, 'bar.o')
    cmd = (
        'gfortran',
        '-arch', 'i386', '-arch', 'x86_64',
        '-c', source_name,
        '-o', object_name,
    )

    cmd_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    result = b'arch flags ignored' not in cmd_output

    shutil.rmtree(temporary_directory)

    return result


class _DualArchitectureCompile(object):
    """Callable wrapper that over-rides ``_compile``.

    Only relevant on OS X. Objects of this type are intended to be used
    to replace / augment to ``_compile`` method on a ``Gnu95FCompiler`` (i.e.
    a Fortran compiler). This is because the Homebrew ``gfortran`` can't
    build fat binaries:

    .. code-block:: console

       $ gfortran -arch i386 -arch x86_64 -c bar.f90 -o bar.o
       gfortran: warning: x86_64 conflicts with i386 (arch flags ignored)

    So instead, this will compile two separate object files and combine them:

    .. code-block:: console

       $ gfortran -arch i386   -c bar.f90 -o ${I386_DIR}/bar.o
       $ gfortran -arch x86_64 -c bar.f90 -o ${X86_64_DIR}/bar.o
       $ lipo ${I386_DIR}/bar.o ${X86_64_DIR}/bar.o -create -output bar.o

    Args:
        f90_compiler (numpy.distutils.fcompiler.gnu.Gnu95FCompiler): A Fortran
            compiler instance.
    """

    def __init__(self, f90_compiler):
        self.f90_compiler = f90_compiler
        self.original_compile = f90_compiler._compile
        self.compiler_cmd = f90_compiler.compiler_f90
        self.arch_index = None  # Set in ``_verify()``.
        self.arch_value = None  # Set in ``_verify()``.
        self._verify()

    def _verify(self):
        """Makes sure the constructor arguments are valid.

        In particular, makes sure that ``f90_compiler`` corresponds to
        ``gfortran`` and that ``compiler_cmd`` has exactly one instance
        of ``-arch``.

        If this succeeds, will set ``arch_index`` and ``arch_value`` on
        the instance.

        Raises:
            TypeError: If ``compiler_cmd`` is not a ``list``.
            TypeError: If ``f90_compiler`` is not a ``Gnu95FCompiler``.
            ValueError: If ``compiler_cmd`` doesn't have exactly one ``-arch``
                segment.
            ValueError: If ``-arch`` is the **last** segment in
                ``compiler_cmd``.
            ValueError: If the ``-arch`` value is not ``i386`` or ``x86_64``.
        """
        from numpy.distutils.fcompiler import gnu

        if not isinstance(self.compiler_cmd, list):
            raise TypeError('Expected a list', self.compiler_cmd)

        if not isinstance(self.f90_compiler, gnu.Gnu95FCompiler):
            raise TypeError('Expected a Gnu95FCompiler', self.f90_compiler)

        if self.compiler_cmd.count('-arch') != 1:
            raise ValueError(
                'Did not find exactly one "-arch" in', self.compiler_cmd)

        arch_index = self.compiler_cmd.index('-arch') + 1
        if arch_index == len(self.compiler_cmd):
            raise ValueError(
                'There is no architecture specified in', self.compiler_cmd)

        arch_value = self.compiler_cmd[arch_index]
        if arch_value not in ('i386', 'x86_64'):
            raise ValueError(
                'Unexpected architecture', arch_value, 'in', self.compiler_cmd)

        self.arch_index = arch_index
        self.arch_value = arch_value

    def _set_architecture(self, architecture):
        """Set the architecture on the Fortran compiler.

        ``compiler_cmd`` is actually a list (mutable), so we can update it here
        and it will change the architecture that ``f90_compiler`` targets.

        Args:
            architecture (str): One of ``i386`` or ``x86_64``.
        """
        self.compiler_cmd[self.arch_index] = architecture

    def _restore_architecture(self):
        """Restore the architecture on the Fortran compiler.

        Resets the ``-arch`` value in ``compiler_cmd`` to its original value.
        """
        self.compiler_cmd[self.arch_index] = self.arch_value

    def __call__(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
        """Call-able replacement for ``_compile``.

        This assumes (but does not verify) that ``original_compile`` has
        no return value.

        Args:
            obj (str): The location of the object file to be created.
            src (str): The location of the source file to be compiled.
            ext (str): The file extension (used to determine flags).
            cc_args (List[str]): Compile args, typically just ``['-c']``.
            extra_postargs (List[str]): Extra arguments at the end of the
                compile command.
            pp_opts (List[str]): Unused by the NumPy ``distutils`` Fortran
                compilers. List of pre-processor options.
        """
        obj_name = os.path.basename(obj)

        # Create a directory and compile an object targeting i386.
        i386_dir = tempfile.mkdtemp(suffix='-i386')
        i386_obj = os.path.join(i386_dir, obj_name)
        self._set_architecture('i386')
        self.original_compile(
            i386_obj, src, ext, cc_args, extra_postargs, pp_opts)

        # Create a directory and compile an object targeting x86_64.
        x86_64_dir = tempfile.mkdtemp(suffix='-x86_64')
        x86_64_obj = os.path.join(x86_64_dir, obj_name)
        self._set_architecture('x86_64')
        self.original_compile(
            x86_64_obj, src, ext, cc_args, extra_postargs, pp_opts)

        # Restore the compiler back to how it was before we modified it.
        self._restore_architecture()

        # Use ``lipo`` to combine the object files into a universal.
        lipo_cmd = ('lipo', i386_obj, x86_64_obj, '-create', '-output', obj)
        self.f90_compiler.spawn(lipo_cmd)

        # Clean up the temporary directories.
        shutil.rmtree(i386_dir)
        shutil.rmtree(x86_64_dir)


def patch_gfortran(f90_compiler):
    """Modify the Fortran compiler to create universal binary object files.

    Does so by patching ``f90_compiler._compile`` with a custom command.

    Patching is only done if:

    * The platform is OS X
    * The current compiler is ``gfortran``
    * The current Python is a universal binary (i.e. dual architecture)
    * The version of ``gfortran`` cannot create universal binaries

    Args:
        f90_compiler (numpy.distutils.fcompiler.FCompiler): A Fortran compiler
            instance.
    """
    from numpy.distutils.fcompiler import gnu

    # Only on OS X.
    if sys.platform != MAC_OS_X:
        return

    # Only with ``gfortran``.
    if not isinstance(f90_compiler, gnu.Gnu95FCompiler):
        return

    # Only if Python is a universal binary.
    if not check_dual_architecture():
        return

    # Only if ``gfortran`` can't produce universal binaries.
    if gfortran_supports_dual_architecture():
        return

    f90_compiler._compile = _DualArchitectureCompile(f90_compiler)


def get_f90_compiler():
    c_compiler = distutils.ccompiler.new_compiler()
    c_compiler.verbose = 2

    f90_compiler = numpy.distutils.fcompiler.new_fcompiler(
        requiref90=True, c_compiler=c_compiler)
    dist = numpy.distutils.core.get_distribution(always=True)
    f90_compiler.customize(dist)
    f90_compiler.verbose = 2

    patch_library_dirs(f90_compiler)
    patch_gfortran(f90_compiler)

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

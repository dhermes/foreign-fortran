import os
import subprocess
import sys

from example import fast


_MAC_OS_X = 'darwin'
_FORTRAN_LIBRARY_PREFIX = 'libraries: ='
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))


foo = fast.foo
make_udf = fast.make_udf
foo_array = fast.foo_array
udf_ptr = fast.udf_ptr
just_print = fast.just_print
view_knob = fast.view_knob
turn_knob = fast.turn_knob


def get_include():
    return os.path.join(PACKAGE_ROOT, 'include')


def get_lib():
    return os.path.join(PACKAGE_ROOT, 'lib')


def _add_gfortran(libraries, library_dirs):
    """Add ``gfortran`` library and library directories.

    This is a "temporary" hack that is problematic because

    * It **assumes** ``gfortran`` is the Fortran compiler, even
      though others would be perfectly fine to use
    * On OS X (at least when installing with Homebrew), ``gcc``
      cannot find ``libgfortran`` on the default path

    Unfortunately, this is needed for ``libexample`` because the
    ``just_print()`` subroutine uses some of the standard library,
    e.g. ``_gfortran_st_write``.
    """
    libraries.append('gfortran')

    # NOTE: This is essentially the same as ``fortran_search_path``
    #       in ``setup.py``.
    if sys.platform != _MAC_OS_X:
        return

    cmd = ('gfortran', '-print-search-dirs')
    cmd_output = subprocess.check_output(cmd).decode('utf-8')

    search_lines = cmd_output.strip().split('\n')
    library_lines = [
        line[len(_FORTRAN_LIBRARY_PREFIX):]
        for line in search_lines
        if line.startswith(_FORTRAN_LIBRARY_PREFIX)
    ]
    if len(library_lines) != 1:
        # NOTE: This means we will fail to update the paths.
        return

    library_line = library_lines[0]
    accepted = set()
    for part in library_line.split(':'):
        full_path = os.path.abspath(part)

        if not os.path.exists(full_path):
            continue

        if os.path.isdir(full_path):
            accepted.add(full_path)

    library_dirs.extend(accepted)


def get_extension_keywords(
        include_dirs=None,
        libraries=None,
        library_dirs=None):
    """Get keyword arguments for a ``setuptools.Extension``.

    This way, an extension can be created that depends on the shared library
    which this library uses. This allows building an extension directly and
    calling the C interface or using ``cimport example.example_fortran`` from
    Cython.

    Each of the arguments are optional. If provided, they will be
    appended to.

    This way, if an extension depends on **other** libraries, the set up can
    be done before calling this function and the lists, e.g. ``libraries``
    can passed in here (and updated).

    Args:
        include_dirs (Optional[List[str]]): List of directories to search for
            C/C++ header files (in Unix form for portability).
        libraries (Optional[List[str]]): List of library names (not filenames
            or paths) to link against.
        library_dirs (Optional[List[str]]): List of directories to search for
            shared libraries at link time.

    Returns:
        Dict[str, List[str]]: Mapping of the keyword arguments. This will
        always contain ``include_dirs``, ``libraries`` and ``library_dirs``.
    """
    if include_dirs is None:
        include_dirs = []
    if libraries is None:
        libraries = []
    if library_dirs is None:
        library_dirs = []

    example_include = get_include()
    example_lib = get_lib()

    include_dirs.append(example_include)
    libraries.append('example')
    library_dirs.append(example_lib)
    _add_gfortran(libraries, library_dirs)

    return {
        'include_dirs': include_dirs,
        'libraries': libraries,
        'library_dirs': library_dirs,
    }

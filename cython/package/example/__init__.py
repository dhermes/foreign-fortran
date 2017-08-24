import os
import sys

from example import fast


_MAC_OS_X = 'darwin'
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))


foo = fast.foo
make_udf = fast.make_udf
foo_array = fast.foo_array
udf_ptr = fast.udf_ptr
just_print = fast.just_print


def get_include():
    return os.path.join(PACKAGE_ROOT, 'include')


def get_lib():
    return os.path.join(PACKAGE_ROOT, '.lib')


def get_extension_keywords(
        include_dirs=None,
        libraries=None,
        library_dirs=None,
        runtime_library_dirs=None,
        extra_link_args=None):
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
        runtime_library_dirs (Optional[List[str]]): List of directories to
            search for shared libraries at run time (for shared extensions,
            this is when the extension is loaded). On Mac OS X, this does not
            work as expected, so instead ``-Wl,-rpath,...`` is used in
            ``extra_link_args``.
        extra_link_args (Optional[List[str]]): Any extra platform- and
            compiler-specific information to use when linking object files
            together to create the extension. This is needed here to provide
            an ``rpath`` in Mac OS X.

    Returns:
        Dict[str, List[str]]: Mapping of the keyword arguments. This will
        always contain ``include_dirs``, ``libraries`` and ``library_dirs``.
        Both keywords ``extra_link_args`` and ``runtime_library_dirs`` will
        be included only if they are non-empty.
    """
    if include_dirs is None:
        include_dirs = []
    if libraries is None:
        libraries = []
    if library_dirs is None:
        library_dirs = []
    if runtime_library_dirs is None:
        runtime_library_dirs = []
    if extra_link_args is None:
        extra_link_args = []

    example_include = get_include()
    example_lib = get_lib()

    include_dirs.append(example_include)
    libraries.append('example')
    library_dirs.append(example_lib)

    if sys.platform == _MAC_OS_X:
        linker_args = ('-Wl', '-rpath', example_lib)
        extra_link_args.append(','.join(linker_args))
    else:
        runtime_library_dirs.append(example_lib)

    keywords = {
        'include_dirs': include_dirs,
        'libraries': libraries,
        'library_dirs': library_dirs,
    }

    if extra_link_args:
        keywords['extra_link_args'] = extra_link_args
    if runtime_library_dirs:
        keywords['runtime_library_dirs'] = runtime_library_dirs

    return keywords

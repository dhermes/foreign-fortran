[`Cython`][1] is a mature and heavily used extension of the Python
programming language. It allows writing optionally typed Python code,
implementing part of a Python module completely in C and many other
performance benefits.

It is **very** mature. For example, a `.pyx` Cython file can be compiled
both to a standard CPython [C extension][2] as well as providing
[basic support][3] for the [PyPy][4] emulation layer `cpyext`.

## Example

```
$ (cd .. && make run-cython)
------------------------------------------------------------
quux = foo(1.0, 16.0) = 61.0
------------------------------------------------------------
quuz = make_udf(1.25, 5.0, 1337)
     = {'broken': 5.0, 'how_many': 1337, 'buzz': 1.25}
------------------------------------------------------------
val =
[[ 3.    4.5 ]
 [ 1.    1.25]
 [ 9.    0.  ]
 [-1.    4.  ]]
two_val = foo_array(val)
two_val =
[[  6.    9. ]
 [  2.    2.5]
 [ 18.    0. ]
 [ -2.    8. ]]
------------------------------------------------------------
made_it = udf_ptr()
        = {'broken': -10.5, 'how_many': 101, 'buzz': 3.125}
------------------------------------------------------------
just_print()
 ======== BEGIN FORTRAN ========
 just_print() was called
 ========  END  FORTRAN ========
------------------------------------------------------------
example.get_include() =
.../foreign-fortran/cython/venv/lib/python.../site-packages/example/include
```

## `sdist` and installed files

On a standard CPython install on a Linux install, a source dist (`sdist`)
contains the following:

```
$ (cd .. && make inspect-cython-sdist)
...

.
├── example-0.0.1
│   ├── example
│   │   ├── example.f90
│   │   ├── example_fortran.pxd
│   │   ├── fast.c
│   │   ├── include
│   │   │   └── example.h
│   │   └── __init__.py
│   ├── PKG-INFO
│   └── setup.py
└── example-0.0.1.tar.gz

3 directories, 8 files
```

Once this gets installed, the following files are present:

```
$ (cd .. && make inspect-cython-installed)
...

.
├── example_fortran.pxd
├── fast.cpython-36m-x86_64-linux-gnu.so
├── include
│   └── example.h
├── __init__.py
└── __pycache__
    └── __init__.cpython-36.pyc

2 directories, 5 files
```

## `cimport`-ing this library

This library provides a `example/example_fortran.pxd` file
that can be used to `cimport` the library without having to
worry about the Python layer:

```
cimport example.example_fortran
```

Currently `cython/use_cimport/wrapper.pyx` is failing because
the Fortran library is not (yet) available:

```
$ (cd .. && make wrap-cython)
...
Traceback (most recent call last):
  File "check_wrapper.py", line 1, in <module>
    import wrapper
ImportError: .../foreign-fortran/cython/use_cimport/wrapper....so: undefined symbol: just_print
```

## Gotcha

However, if `libraries=['gfortran']` is not specified in `setup.py` when
building the CPython C extension module (`example.so`), then the print
statements in `just_print` (as defined in in `example.f90`) cause

```
$ (cd .. && make broken-cython)
cd cython/ && \
  IGNORE_LIBRARIES=true python setup.py build_ext --inplace && \
  python -c 'import example'
running build_ext
skipping 'example.c' Cython extension (up-to-date)
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ImportError: .../cython/example...so: undefined symbol: _gfortran_transfer_character_write
Makefile:93: recipe for target 'broken-cython' failed
make: *** [broken-cython] Error 1
```

## References

- Decently [helpful article][5] and ["pre-article"][6] to that one about
  using Cython to wrap Fortran. But this article fails to point out
  its approach can leave out some symbols (e.g. the `check_cython`
  example when `libgfortran` isn't included)
- Description on the uber-useful `fortran90.org` on
  [how to interface with C][7]

[1]: https://cython.readthedocs.io/
[2]: https://docs.python.org/3.6/extending/extending.html
[3]: https://cython.readthedocs.io/en/latest/src/userguide/pypy.html
[4]: https://pypy.org/
[5]: https://maurow.bitbucket.io/notes/calling_fortran_from_python.html
[6]: https://maurow.bitbucket.io/notes/calling_fortran_from_c.html
[7]: http://www.fortran90.org/src/best-practices.html#interfacing-with-c

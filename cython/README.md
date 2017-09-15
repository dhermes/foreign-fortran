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
------------------------------------------------------------
view_knob() = 1337
turn_knob(42)
view_knob() = 42
```

## `sdist` and installed files

On a standard CPython install on a Linux install, a source dist (`sdist`)
contains the following:

```
$ (cd .. && make inspect-cython-sdist)
.
├── example
│   ├── example.f90
│   ├── example_fortran.pxd
│   ├── fast.c
│   ├── include
│   │   └── example.h
│   └── __init__.py
├── example.egg-info
│   ├── dependency_links.txt
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   └── top_level.txt
├── MANIFEST.in
├── PKG-INFO
├── setup.cfg
└── setup.py

3 directories, 13 files
```

Once this gets installed, the following files are present:

```
$ (cd .. && make inspect-cython-installed)
.
├── example_fortran.pxd
├── fast.cpython-36m-x86_64-linux-gnu.so
├── include
│   └── example.h
├── __init__.py
├── lib
│   └── libexample.a
└── __pycache__
    └── __init__.cpython-36.pyc

3 directories, 6 files
```

## `cimport`-ing this library

This library provides a `example/example_fortran.pxd` file
that can be used to `cimport` the library without having to
worry about the Python layer:

```
cimport example.example_fortran
```

In this case, the library referenced in `example_fortran.pxd`
is made available in the `example` package:

```python
>>> import os
>>> import example
>>>
>>> include_dir = example.get_include()
>>> include_dir
'.../foreign-fortran/cython/venv/lib/python.../site-packages/example/include'
>>> os.listdir(include_dir)
['example.h']
>>>
>>> lib_dir = example.get_lib()
>>> lib_dir
'.../foreign-fortran/cython/venv/lib/python.../site-packages/example/lib'
>>> os.listdir(lib_dir)
['libexample.a']
```

See `cython/use_cimport/setup.py` for an example of how to wrap:

```
$ (cd .. && make wrap-cython)
>>> wrapper.morp()
 ======== BEGIN FORTRAN ========
 just_print() was called
 ========  END  FORTRAN ========
>>> example.foo(1.5, 2.5)
10.875
>>> wrapper.triple_foo(1.5, 2.5)
32.625
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
...
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File ".../cython/package/example/__init__.py", line 5, in <module>
    from example import fast
ImportError: .../cython/package/example/fast...so: undefined symbol: _gfortran_transfer_character_write
Makefile:119: recipe for target 'broken-cython' failed
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

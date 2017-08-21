Rather than calling into a shared library via `ctypes` or
`cffi`, the [`f2py`][1] tool can be used to to wrap Fortran
interfaces in Python functions. It does this by generating
a custom CPython [C extension][2] and compiling it with a
Fortran shared library.

`f2py` has many limitations, chief of which is absence of support
for user-defined types or derived types (equivalent of a C `struct`).
The examples below demonstrate a few ways of getting around these
limitations, including manual conversion of a custom typed variable
to raw bytes.

## Example

```
$ (cd .. && make run-f2py)
------------------------------------------------------------
example: <module 'example' from '.../f2py/example...so'>
dir(example.example): foo, foo_array, foo_by_ref, just_print, make_udf, udf_ptr
------------------------------------------------------------
foo       (1.0, 16.0) = 0.0
foo_by_ref(1.0, 16.0) = 61.0
------------------------------------------------------------
quuz = make_udf(1.25, 5.0, 1337)
     = UserDefined(buzz=1.25, broken=5.0, how_many=1337)
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
ptr_as_int = address(made_it)  # intptr_t / ssize_t / long
ptr_as_int = 139859191412464  # 0x7f33816c36f0
udf_ptr(ptr_as_int)  # Set memory in ``made_it``
made_it = UserDefined(buzz=3.125, broken=-10.5, how_many=101)
------------------------------------------------------------
just_print()
 ======== BEGIN FORTRAN ========
 just_print() was called
 ========  END  FORTRAN ========
```

## What is Happening?

`f2py` actually generates a wrapped `{modname}module.c` file and
utilizes a `fortranobject` C library to create CPython C extensions:

```python
>>> import os
>>> import numpy.f2py.src
>>>
>>> f2py_dir = os.path.dirname(numpy.f2py.__file__)
>>> f2py_dir
'.../lib/python3.6/site-packages/numpy/f2py'
>>> os.listdir(os.path.join(f2py_dir, 'src'))
['fortranobject.c', 'fortranobject.h']
```

It uses a C compiler with flags determined by `distutils` to
link against NumPy and Python headers when compiling `{modname}module.c`
and `fortranobject.c` and uses a Fortran compiler for `{modname}.f90`.
Then it uses the Fortran compiler as linker:

```
gfortran \
  -Wall \
  -g \
  -shared \
  ${TEMPDIR}/.../{modname}module.o \
  ${TEMPDIR}/.../fortranobject.o \
  ${TEMPDIR}/{modname}.o \
  -lgfortran \
  -o \
  ./{modname}.so
```

## Failure

When trying to convert a Fortran subroutine to Python via `f2py`, a
problem occurs if the subroutine uses a user-defined type:

```
$ (cd .. && make broken-f2py)
cd f2py/ && \
  f2py \
    --verbose \
    -c \
    --opt='-O3' \
    -m example \
    ../fortran/example.f90 \
    only: make_container
...
Building modules...
        Building module "fortran_example"...
                Constructing F90 module support for "example"...
Skipping type unknown_type
Skipping type unknown_type
                        Constructing wrapper function "example.make_container"...
getctype: No C-type found in "{'attrspec': [], 'typename': 'userdefined', 'intent': ['out'], 'typespec': 'type'}", assuming void.
getctype: No C-type found in "{'attrspec': [], 'typename': 'userdefined', 'intent': ['out'], 'typespec': 'type'}", assuming void.
getctype: No C-type found in "{'attrspec': [], 'typename': 'userdefined', 'intent': ['out'], 'typespec': 'type'}", assuming void.
Traceback (most recent call last):
...
  File ".../numpy/f2py/capi_maps.py", line 417, in getpydocsign
    sig = '%s : %s %s%s' % (a, opt, c2py_map[ctype], init)
KeyError: 'void'
Makefile:69: recipe for target 'broken-f2py' failed
make: *** [broken-f2py] Error 1
```

## References

- (Lack of) support [in `f2py`][3]
- The [`f90wrap`][4] library seeks to work around the lack of
  `f2py` support for user-defined types. The library does not appear (at
  first glance) to be as mature / production-ready as `f2py`.

[1]: https://docs.scipy.org/doc/numpy/f2py/usage.html
[2]: https://docs.python.org/3.6/extending/extending.html
[3]: https://mail.scipy.org/pipermail/scipy-user/2008-December/018881.html
[4]: https://github.com/jameskermode/f90wrap

# Playing around with "user defined types" in Fortran

## What goes wrong?

When trying to convert a Fortran subroutine to Python via `f2py`, a
problem occurs if the subroutine uses a user-defined type:

```
$ make broken-f2py
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

## Doing Everything

Run the exact same Fortran code in six different ways:

- [Fortran][8]
- [C][9]
- Python with [`ctypes`][10]
- Python with [`cffi`][11]
- Python with `f2py`
- Cython

### Python via `f2py`

```
$ make run-f2py
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

### Python via Cython

```
$ make run-cython
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
```

However, if `libraries=['gfortran']` is not specified in `setup.py` when
building the module (`example.so`), then the print statements in
`just_print` (as defined in in `example.f90`) cause

```
$ make example.so > /dev/null 2>&1; python check_cython.py; make clean > /dev/null
Traceback (most recent call last):
  File "check_cython.py", line 4, in <module>
    import example
ImportError: .../example.so: undefined symbol: _gfortran_transfer_character_write
```

## References

- (Lack of) support [in `f2py`][3] (and possible workaround [`f90wrap`][4])
- Decently [helpful article][5] and ["pre-article"][6] to that one about
  using Cython to wrap Fortran (rather than `f2py`). But this article fails
  to point out it's approach can leave out some symbols (e.g. the `check_cython`
  example when `libgfortran` isn't included)
- Description on the uber-useful `fortran90.org` on [how to interface with C][7]

[3]: https://mail.scipy.org/pipermail/scipy-user/2008-December/018881.html
[4]: https://github.com/jameskermode/f90wrap
[5]: https://maurow.bitbucket.io/notes/calling_fortran_from_python.html
[6]: https://maurow.bitbucket.io/notes/calling_fortran_from_c.html
[7]: http://www.fortran90.org/src/best-practices.html#interfacing-with-c
[8]: fortran/README.md
[9]: c/README.md
[10]: python/README.md#ctypes
[11]: python/README.md#cffi

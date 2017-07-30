# Playing around with "user defined types" in Fortran

## What goes wrong?

When trying to convert a Fortran subroutine to Python via `f2py`, a
problem occurs if the subroutine uses a user-defined type:

```
$ make fortran_broken
f2py --verbose -c --opt='-O3' -m fortran_example example.f90 \
only: make_udf
...
Building modules...
        Building module "fortran_example"...
                Constructing F90 module support for "example"...
Skipping type unknown_type
                        Constructing wrapper function "example.make_udf"...
getctype: No C-type found in "{'attrspec': [], 'typename': 'userdefined', 'intent': ['out'], 'typespec': 'type'}", assuming void.
getctype: No C-type found in "{'attrspec': [], 'typename': 'userdefined', 'intent': ['out'], 'typespec': 'type'}", assuming void.
getctype: No C-type found in "{'attrspec': [], 'typename': 'userdefined', 'intent': ['out'], 'typespec': 'type'}", assuming void.
Traceback (most recent call last):
...
  File ".../numpy/f2py/capi_maps.py", line 412, in getpydocsign
    sig = '%s : %s %s%s' % (a, opt, c2py_map[ctype], init)
KeyError: 'void'
Makefile:24: recipe for target 'fortran_broken' failed
make: *** [fortran_broken] Error 1
```

## Doing Everything

Run the exact same Fortran code in five different ways:

### Plain Fortran

```
$ make main > /dev/null; ./main; make clean > /dev/null
 foo(   1.0000000000000000        16.000000000000000      ) =    61.000000000000000
 make_udf(   1.2500000000000000        5.0000000000000000             1337 )
        =    1.2500000000000000        5.0000000000000000             1337
 foo_array(
                4 ,
     [[   3.0000000000000000        4.5000000000000000      ],
      [   1.0000000000000000        1.2500000000000000      ],
      [   9.0000000000000000        0.0000000000000000      ],
      [  -1.0000000000000000        4.0000000000000000      ]],
 ) =
     [[   6.0000000000000000        9.0000000000000000      ],
      [   2.0000000000000000        2.5000000000000000      ],
      [   18.000000000000000        0.0000000000000000      ],
      [  -2.0000000000000000        8.0000000000000000      ]]
```

### Plain C


```
$ make main_c > /dev/null; ./main_c; make clean > /dev/null
--------------------------------------------------------------
quux = foo(1.000000, 16.000000) = 61.000000
--------------------------------------------------------------
quuz = make_udf(1.250000, 5.000000, 1337)
     = UserDefined(1.250000, 5.000000, 1337)
--------------------------------------------------------------
foo_array(
    4,
    [[3.000000, 4.500000],
     [1.000000, 1.250000],
     [9.000000, 0.000000],
     [-1.000000, 4.000000]],
) =
    [[6.000000, 9.000000],
     [2.000000, 2.500000],
     [18.000000, 0.000000],
     [-2.000000, 8.000000]]
--------------------------------------------------------------
ptr_as_int = 140734382282800 (0x7fff46dd1830)
made_it = UserDefined(3.125000, -10.500000, 101)
```

### Python via `ctypes`


```
$ make example.so > /dev/null; python check_ctypes.py; make clean > /dev/null
------------------------------------------------------------
<CDLL '.../example.so', handle 16e1440 at 7f2491f75350>
------------------------------------------------------------
quux = foo(c_double(1.0), c_double(16.0)) = c_double(61.0)
------------------------------------------------------------
quuz = make_udf(c_double(1.25), c_double(5.0), c_int(1337))
     = UserDefined(buzz=1.25, broken=5.0, how_many=1337)
quuz needsfree: True
address(quuz) = 26217808
*address(quuz) = UserDefined(buzz=1.25, broken=5.0, how_many=1337)
------------------------------------------------------------
val =
[[ 3.    4.5 ]
 [ 1.    1.25]
 [ 9.    0.  ]
 [-1.    4.  ]]
two_val = foo_array(c_int(4), val)
two_val =
[[  6.    9. ]
 [  2.    2.5]
 [ 18.    0. ]
 [ -2.    8. ]]
------------------------------------------------------------
ptr_as_int: c_long(26228288)
made_it: UserDefined(buzz=3.125, broken=-10.5, how_many=101)
made_it needsfree: True
*address = UserDefined(buzz=3.125, broken=-10.5, how_many=101)
```

### Python via `f2py`

```
$ make fortran_example.so > /dev/null; python check_f2py.py; make clean > /dev/null
------------------------------------------------------------
fortran_example: <module 'fortran_example' from '.../fortran_example.so'>
dir(fortran_example.example): ['foo', 'foo_array', 'foo_by_ref', 'udf_ptr']
------------------------------------------------------------
foo       (1.0, 16.0) = 0.0
foo_by_ref(1.0, 16.0) = 61.0
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
ptr_as_int = address(made_it)  # long
ptr_as_int = 43660048
udf_ptr(ptr_as_int)  # Set memory in ``made_it``
made_it = UserDefined(buzz=3.125, broken=-10.5, how_many=101)
```

### Python via Cython

```
$ make cy_example.so > /dev/null 2>&1; python check_cython.py; make clean > /dev/null
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
```

## References

- [Examples][1]
- StackOverflow [question][2] about user-defined types
- (Lack of) support [in `f2py`][3] (and possible workaround [`f90wrap`][4])
- Decently [helpful article][5] and ["pre-article"][6] to that one about
  using Cython to wrap Fortran (rather than `f2py`)

[1]: http://www.mathcs.emory.edu/~cheung/Courses/561/Syllabus/6-Fortran/struct.html
[2]: https://stackoverflow.com/q/8557244
[3]: https://mail.scipy.org/pipermail/scipy-user/2008-December/018881.html
[4]: https://github.com/jameskermode/f90wrap
[5]: https://maurow.bitbucket.io/notes/calling_fortran_from_python.html
[6]: https://maurow.bitbucket.io/notes/calling_fortran_from_c.html

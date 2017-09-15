The "simplest" and most portable way to call Fortran from any
language, including Python, is to make a shared library (via `-fPIC`,
i.e. "position independent code").

With Python, calling a shared library is possible with
[`ctypes`][1] and [`cffi`][2]:

## `ctypes`


```
$ (cd .. && make run-ctypes)
------------------------------------------------------------
<CDLL '.../python/example.so', handle e757b0 at 0x7ff4d3effb38>
------------------------------------------------------------
quux = foo(c_double(1.0), c_double(16.0)) = c_double(61.0)
------------------------------------------------------------
quuz = make_udf(c_double(1.25), c_double(5.0), c_int(1337))
     = UserDefined(buzz=1.25, broken=5.0, how_many=1337)
needsfree(quuz) = True
address(quuz) = 140689106863712  # 0x7ff4bc3d0660
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
ptr_as_int = address(made_it)  # intptr_t / ssize_t / long
ptr_as_int = c_long(140689106863736)  # 0x7ff4bc3d0678
udf_ptr(ptr_as_int)  # Set memory in ``made_it``
made_it = UserDefined(buzz=3.125, broken=-10.5, how_many=101)
needsfree(made_it) = True
*ptr_as_int = UserDefined(buzz=3.125, broken=-10.5, how_many=101)
------------------------------------------------------------
contained =
[[ 0.  4.]
 [ 1.  9.]
 [ 1.  2.]
 [ 3.  1.]]
container = make_container(contained)
container.data =
[[ 0.  4.]
 [ 1.  9.]
 [ 1.  2.]
 [ 3.  1.]]
address(contained)      = 15107312  # 0xe684f0
address(container)      = 140689100733808  # 0x7ff4bbdf7d70
address(container.data) = 140689100733808  # 0x7ff4bbdf7d70
------------------------------------------------------------
just_print()
 ======== BEGIN FORTRAN ========
 just_print() was called
 ========  END  FORTRAN ========
------------------------------------------------------------
view_knob() = 1337
turn_knob(c_int(42))
view_knob() = 42
```

## `cffi`

```
$ (cd .. && make run-cffi)
------------------------------------------------------------
quux = foo(1.0, 16.0) = 61.0
------------------------------------------------------------
quuz = make_udf(1.25, 5.0, 1337)
     = UserDefined(1.25, 5.0, 1337)
------------------------------------------------------------
val =
[[ 3.    4.5 ]
 [ 1.    1.25]
 [ 9.    0.  ]
 [-1.    4.  ]]
two_val = foo_array(4, val)
two_val =
[[  6.    9. ]
 [  2.    2.5]
 [ 18.    0. ]
 [ -2.    8. ]]
------------------------------------------------------------
ptr_as_int = address(made_it)  # intptr_t / ssize_t / long
ptr_as_int = 32091392  # 0x1e9ad00
udf_ptr(ptr_as_int)  # Set memory in ``made_it``
made_it = UserDefined(3.125, -10.5, 101)
------------------------------------------------------------
just_print()
 ======== BEGIN FORTRAN ========
 just_print() was called
 ========  END  FORTRAN ========
------------------------------------------------------------
view_knob() = 1337
turn_knob(42)
view_knob() = 42
```

[1]: https://docs.python.org/3/library/ctypes.html
[2]: https://cffi.readthedocs.io/

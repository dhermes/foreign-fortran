This is the most vanilla example of all. We are simply
calling the Fortran `example` module from a Fortran program:

```
$ (cd .. && make run-fortran)
------------------------------------------------------------
quux = foo(1.000000, 16.000000) = 61.000000
------------------------------------------------------------
quuz = make_udf(1.250000, 5.000000, 1337)
     = UserDefined(1.250000, 5.000000, 1337)
------------------------------------------------------------
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
------------------------------------------------------------
ptr_as_int = c_loc(made_it)  ! type(c_ptr) / integer(c_intptr_t) / integer(kind=8)
ptr_as_int = 140726916390992  ! 0x7FFD89DCA050
udf_ptr(ptr_as_int)  ! Set memory in ``made_it``
made_it = UserDefined(3.125000, -10.500000, 101)
------------------------------------------------------------
just_print()
 ======== BEGIN FORTRAN ========
 just_print() was called
 ========  END  FORTRAN ========
```

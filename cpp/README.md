We run many of the subroutines in the `example` Fortran module
(`../fortran/example.f90`) directly from C++:


```
$ (cd .. && make run-cpp)
------------------------------------------------------------
quux = foo(1.000000, 16.000000) = 61.000000
------------------------------------------------------------
quuz = make_udf(1.250000, 5.000000, 1337)
     = UserDefined(1.250000, 5.000000, 1337)
------------------------------------------------------------
just_print()
 ======== BEGIN FORTRAN ========
 just_print() was called
 ========  END  FORTRAN ========
```

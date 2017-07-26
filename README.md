Playing around with "user defined types" in Fortran.

Some related references:

- [Examples][1]
- StackOverflow [question][2] about user-defined types
- (Lack of) support [in `f2py`][3] (and possible workaround [`f90wrap`][4])

When trying to convert a Fortran subroutine to Python via `f2py`, a
problem occurs if the subroutine uses a user-defined type:

```
$ make fortran_example.so
...
Skipping type userdefined
                        Constructing wrapper function "example.foo"...
                          quux = foo(bar,baz)
                        Constructing wrapper function "example.make_udf"...
getctype: No C-type found in "{'attrspec': [], 'typename': 'userdefined', 'intent': ['out'], 'typespec': 'type'}", assuming void.
getctype: No C-type found in "{'attrspec': [], 'typename': 'userdefined', 'intent': ['out'], 'typespec': 'type'}", assuming void.
getctype: No C-type found in "{'attrspec': [], 'typename': 'userdefined', 'intent': ['out'], 'typespec': 'type'}", assuming void.
Traceback (most recent call last):
...
  File ".../numpy/f2py/capi_maps.py", line 412, in getpydocsign
    sig = '%s : %s %s%s' % (a, opt, c2py_map[ctype], init)
KeyError: 'void'
Makefile:7: recipe for target 'fortran_example.so' failed
make: *** [fortran_example.so] Error 1
```

Decently [helpful article][5] and ["pre-article"][6] to that one.

## Doing Everything

```
$ make main main_c example.so fortran_example.so
```

then run the exact same Fortran code in four different ways:

```
$ ./main
 bar =   1.0000000000000000
 baz =   16.000000000000000
 quux =   61.000000000000000
   1.2500000000000000        5.0000000000000000             1337
$ ./main_c
quux = foo(1.000000, 16.000000) = 61.000000
$ python ctypes_static.py
<CDLL '.../example.so', handle 16e1440 at 7f2491f75350>
bar = c_double(1.0)
baz = c_double(16.0)
quux = c_double(61.0)
$ python check_fortran_extension.py
fortran_example: <module 'fortran_example' from '/home/dhermes/Desktop/fortran-user-defined-types/fortran_example.so'>
fortran_example.example: <fortran object>
dir(fortran_example.example): ['foo', 'foo_not_c']
fortran_example.example.foo      (1.0, 16.0) = 0.0
fortran_example.example.foo_not_c(1.0, 16.0) = 61.0
```

[1]: http://www.mathcs.emory.edu/~cheung/Courses/561/Syllabus/6-Fortran/struct.html
[2]: https://stackoverflow.com/q/8557244
[3]: https://mail.scipy.org/pipermail/scipy-user/2008-December/018881.html
[4]: https://github.com/jameskermode/f90wrap
[5]: https://maurow.bitbucket.io/notes/calling_fortran_from_python.html
[6]: https://maurow.bitbucket.io/notes/calling_fortran_from_c.html

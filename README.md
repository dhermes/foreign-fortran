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

[1]: http://www.mathcs.emory.edu/~cheung/Courses/561/Syllabus/6-Fortran/struct.html
[2]: https://stackoverflow.com/q/8557244
[3]: https://mail.scipy.org/pipermail/scipy-user/2008-December/018881.html
[4]: https://github.com/jameskermode/f90wrap
[5]: https://maurow.bitbucket.io/notes/calling_fortran_from_python.html
[6]: https://maurow.bitbucket.io/notes/calling_fortran_from_c.html

Fortran can be invoked directly from [Go][1] code by using [`cgo`][2].
A simple [example][3] is provided in the Golang source tree, which
is quite helpful. If the Fortran source is in the same directory as
as a Go library, `cgo` automatically builds the Fortran files and
includes them. This **does not** work quite the same when the package
is `main`, so we have instead made a "fake" `golang/src` directory
with the `example` package.

To see our `example` Fortran module in action:

```
$ (cd .. && make run-golang)
------------------------------------------------------------
quux = foo(1.000000, 16.000000) = 61.000000
------------------------------------------------------------
quuz = make_udf(1.250000, 5.000000, 1337)
     = *example.UserDefined(1.250000, 5.000000, 1337)
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
just_print()
 ======== BEGIN FORTRAN ========
 just_print() was called
 ========  END  FORTRAN ========
```

[1]: https://golang.org/
[2]: https://golang.org/cmd/cgo/
[3]: https://golang.org/misc/cgo/fortran/

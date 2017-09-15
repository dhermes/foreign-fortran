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
ptrAsInt = &madeIt
ptrAsInt = 842350511456  // 0xc42000c560
udf_ptr(&ptrAsInt)  // Set memory in ``madeIt``
&madeIt = *example.UserDefined(3.125000, -10.500000, 101)
------------------------------------------------------------
contained =
  [[0.000000, 4.000000],
   [1.000000, 9.000000],
   [1.000000, 2.000000],
   [3.000000, 1.000000]]
container = make_container(contained)
container.Data =
  [[0.000000, 4.000000],
   [1.000000, 9.000000],
   [1.000000, 2.000000],
   [3.000000, 1.000000]]
&contained      = 842350544192  // 0xc420014540
&container      = 842350518320  // 0xc42000e030
 container.Data = 842350544256  // 0xc420014580
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

[1]: https://golang.org/
[2]: https://golang.org/cmd/cgo/
[3]: https://golang.org/misc/cgo/fortran/

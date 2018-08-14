##
Go
##

Fortran can be invoked directly from `Go`_ code by using the ``cgo``
`language extension`_. A simple `example`_ is provided in the Golang
source tree, which is quite helpful. If the Fortran source is in the
same directory as a Go library, ``cgo`` automatically builds the Fortran
files and includes them.

.. _Go: https://golang.org/
.. _language extension: https://golang.org/cmd/cgo/
.. _example: https://golang.org/misc/cgo/fortran/

We define the Go package ``example`` in the ``golang/src`` directory. The
Fortran source and the C headers are side-by-side with the Go package:

.. code-block:: console

   $ tree golang/src/example/
   golang/src/example/
   ├── example.f90 -> ../../../fortran/example.f90
   ├── example.go
   └── example.h -> ../../../c/example.h

   0 directories, 3 files

*******
Package
*******

Within the package, we first declare the package to use ``cgo`` and
include the relevant header file:

.. literalinclude:: ../golang/src/example/example.go
   :language: go
   :lines: 8-9

We start by defining user-friendly equivalents of ``C.struct_UserDefined`` and
``C.struct_DataContainer``

.. literalinclude:: ../golang/src/example/example.go
   :language: go
   :lines: 11-26

Adding :c:func:`just_print` to the package interface is just a matter of
making ``C.just_print`` public:

.. literalinclude:: ../golang/src/example/example.go
   :language: go
   :lines: 28-30

When passing in ``*float64`` (i.e. pointer types), the underlying
values can be passed along to ``C.make_udf`` without having to copy
any data, e.g. via ``(*C.double)(buzz)``. The foreign call will populate
the fields of a ``C.struct_UserDefined``, which will need to be converted
to normal Go types when a ``UserDefined`` value is created for the return.
To avoid copying when constructing a ``UserDefined`` object, we dereference
a field value (e.g. ``&quuz.buzz``), convert the reference to a non-``C``
pointer type (e.g. ``(*float64)(&quuz.buzz)``) and then dereference the
value:

.. literalinclude:: ../golang/src/example/example.go
   :language: go
   :lines: 46-59

When dealing with array types, the first value in a slice is dereferenced and
then converted into a C pointer (e.g. ``(*C.double)(&val[0])``):

.. literalinclude:: ../golang/src/example/example.go
   :language: go
   :lines: 61-69

When calling :c:func:`udf_ptr`, a ``UserDefined`` value must be created,
dereferenced, cast to ``unsafe.Pointer`` and then cast again to ``uintptr``:

.. literalinclude:: ../golang/main.go
   :language: go
   :dedent: 1
   :lines: 50-52

Only then can the ``uintptr`` be converted to a ``C.intptr_t``:

.. literalinclude:: ../golang/src/example/example.go
   :language: go
   :lines: 71-85

In the case of ``view_knob()``, the mangled name must be used:

.. literalinclude:: ../golang/src/example/example.go
   :language: go
   :lines: 87,90-98

******
Output
******

The Go example can be run via ``go run``. As with :doc:`c` and :doc:`cpp`, the
``gfortran`` search path may need to be explicitly provided (with ``-L`` flags). This
can be done with the ``CGO_LDFLAGS`` environment variable.

.. code-block:: console

   $ go run golang/main.go
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
   ptrAsInt = 842350544096  // 0xc4200144e0
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
   &contained      = 842350560256  // 0xc420018400
   &container      = 842350518320  // 0xc42000e030
    container.Data = 842350560320  // 0xc420018440
   ------------------------------------------------------------
   just_print()
    ======== BEGIN FORTRAN ========
    just_print() was called
    ========  END  FORTRAN ========
   ------------------------------------------------------------
   view_knob() = 1337
   turn_knob(42)
   view_knob() = 42

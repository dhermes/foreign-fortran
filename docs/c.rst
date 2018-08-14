#
C
#

This example interacts with the  `object <module.html#build>`__ file
``fortran/example.o`` when creating the executable ``c_example``. Since
the example will use :c:func:`just_print`, it relies on ``libgfortran``
so we link against it (potentially having used ``gfortran -print-search-dirs``
to determine where it is located):

.. code-block:: console

   $ gcc \
   >   c/example.c \
   >   fortran/example.o \
   >   -o c_example \
   >   -L/usr/lib/x86_64-linux-gnu \
   >   -L/usr/lib/x86_64-linux-gnu \
   >   -lgfortran

Alternatively, ``gfortran`` can consume a ``c/example.o`` object file created
from the C source. This removes the worry of including ``libgfortran`` though
it's somewhat strange to compile an executable from C code with a Fortran
compiler.

.. code-block:: console

   $ gcc \
   >   -I c/ \
   >   -c c/example.c \
   >   -o c/example.o
   $ gfortran \
   >   c/example.o \
   >   fortran/example.o \
   >   -o c_example

Finally, we run ``c_example`` to verify the behavior of
several procedures in the public interface:

.. code-block:: console

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
   ptr_as_int = &made_it  // intptr_t
                          // ssize_t
                          // long
   ptr_as_int = 140727221075056  // 0x7ffd9c05bc70
   udf_ptr(ptr_as_int)  // Set memory in ``made_it``
   made_it = UserDefined(3.125000, -10.500000, 101)
   ------------------------------------------------------------
   contained =
     [[0.000000, 4.000000],
      [1.000000, 9.000000],
      [1.000000, 2.000000],
      [3.000000, 1.000000]]
   container = make_container(contained)
   container.data =
     [[0.000000, 4.000000],
      [1.000000, 9.000000],
      [1.000000, 2.000000],
      [3.000000, 1.000000]]
   &contained      = 140727221075216  // 0x7ffd9c05bd10
   &container      = 140727221075280  // 0x7ffd9c05bd50
   &container.data = 140727221075280  // 0x7ffd9c05bd50
   ------------------------------------------------------------
   just_print()
    ======== BEGIN FORTRAN ========
    just_print() was called
    ========  END  FORTRAN ========
   ------------------------------------------------------------
   view_knob() = 1337
   turn_knob(42)
   view_knob() = 42

Note that in order to call ``view_knob()``, the mangled name must
be used

.. literalinclude:: ../c/example.c
   :language: c
   :lines: 10,13-14

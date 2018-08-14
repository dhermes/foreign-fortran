###
C++
###

This example interacts with the  `object <module.html#build>`__ file
``fortran/example.o`` when creating the executable ``cpp_example``. Since
the example will use :c:func:`just_print`, it relies on ``libgfortran``
so we link against it (potentially having used ``gfortran -print-search-dirs``
to determine where it is located):

.. code-block:: console

   $ g++ \
   >   -std=c++11 \
   >   -I c/ \
   >   cpp/example.cpp \
   >   fortran/example.o \
   >   -o cpp_example \
   >   -L/usr/lib/gcc/x86_64-linux-gnu/5 \
   >   -L/usr/lib/x86_64-linux-gnu \
   >   -lgfortran

The calling script in C++ is only partially complete:

.. code-block:: console

   $ ./cpp_example
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

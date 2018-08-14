###
C++
###

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

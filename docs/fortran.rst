#######
Fortran
#######

This is the most vanilla example of all. We are simply
calling the Fortran ``example`` module from a Fortran program.

The module is only "foreign" in the sense that we only
interact with the  `object <module.html#build>`__ file ``example.o``
when creating the executable ``fortran_example``:

.. code-block:: console

   $ gfortran \
   >   -o fortran_example \
   >   fortran/main.f90 \
   >   fortran/example.o

However, this still requires the presence of a module file to build
the executable

.. code-block:: console

   $ ls fortran/example.mod
   fortran/example.mod
   $ rm -f fortran/example.mod
   $ gfortran \
   >   -o fortran_example \
   >   fortran/main.f90 \
   >   fortran/example.o
   fortran/main.f90:4:6:

      use example, only: &
         1
   Fatal Error: Can't open module file 'example.mod' for reading
     at (1): No such file or directory
   compilation terminated.

Finally, we run ``fortran_example`` to verify the behavior of
several procedures in the public interface:

.. code-block:: console

   $ ./fortran_example
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
   ptr_as_int = c_loc(made_it)  ! type(c_ptr)
                                ! integer(c_intptr_t)
                                ! integer(kind=8)
   ptr_as_int = 140733727194752  ! 0x7FFF1FD13E80
   udf_ptr(ptr_as_int)  ! Set memory in ``made_it``
   made_it = UserDefined(3.125000, -10.500000, 101)
   ------------------------------------------------------------
   just_print()
    ======== BEGIN FORTRAN ========
    just_print() was called
    ========  END  FORTRAN ========
   ------------------------------------------------------------
   view_knob() = 1337
   turn_knob(42)
   view_knob() = 42

Using the shared library is as simple as declaring the public
symbols used:

.. literalinclude:: ../fortran/main.f90
   :language: fortran
   :dedent: 2
   :lines: 4-6

Notice that the ``view_knob()`` subroutine is in the public
**Fortran** interface even though it doesn't have a bound
name in the ABI.

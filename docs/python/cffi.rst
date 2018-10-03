########
``cffi``
########

This example interacts with the  `shared object <../module.html#shared-object>`__
file ``fortran/example.so``. Similar to ``ctypes``, the ``cffi`` `library`_
enables the creation of a foreign function interface (FFI) via ``dlopen``:

.. _library: https://cffi.readthedocs.io/

.. code-block:: python

   >>> import cffi
   >>> ffi = cffi.FFI()
   >>> so_file = "fortran/example.so"
   >>> lib_example = ffi.dlopen(so_file)
   >>> lib_example
   <cffi.api._make_ffi_library.<locals>.FFILibrary object at 0x7fdd0e364ba8>

After dynamically loading the path, we need to manually define each
member of the ABI that we'll use (both the functions and the structs):

.. literalinclude:: ../../python/check_cffi.py
   :language: python
   :dedent: 4
   :lines: 30-46

In order to convert a NumPy array to a type that can be used with ``cffi``,
we use the existing ``ctypes`` interface:

.. literalinclude:: ../../python/check_cffi.py
   :language: python
   :lines: 18-21

******
Output
******

.. code-block:: console

   $ python python/check_cffi.py
   ------------------------------------------------------------
   quux = foo(1.0, 16.0) = 61.0
   ------------------------------------------------------------
   quuz = make_udf(1.25, 5.0, 1337)
        = UserDefined(1.25, 5.0, 1337)
   ------------------------------------------------------------
   val =
   [[ 3.    4.5 ]
    [ 1.    1.25]
    [ 9.    0.  ]
    [-1.    4.  ]]
   two_val = foo_array(4, val)
   two_val =
   [[ 6.   9. ]
    [ 2.   2.5]
    [18.   0. ]
    [-2.   8. ]]
   ------------------------------------------------------------
   ptr_as_int = address(made_it)  # intptr_t / ssize_t / long
   ptr_as_int = 14735136  # 0xe0d720
   udf_ptr(ptr_as_int)  # Set memory in ``made_it``
   made_it = UserDefined(3.125, -10.5, 101)
   ------------------------------------------------------------
   just_print()
    ======== BEGIN FORTRAN ========
    just_print() was called
    ========  END  FORTRAN ========
   ------------------------------------------------------------
   view_knob() = 1337
   turn_knob(42)
   view_knob() = 42

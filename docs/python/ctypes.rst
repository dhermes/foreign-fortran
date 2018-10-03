##########
``ctypes``
##########

This example interacts with the  `shared object <../module.html#shared-object>`__
file ``fortran/example.so``. This shared object file can be loaded directly

.. code-block:: python

   >>> import ctypes
   >>> so_file = "fortran/example.so"
   >>> lib_example = ctypes.cdll.LoadLibrary(so_file)
   >>> lib_example
   <CDLL 'fortran/example.so', handle 1b8d1b0 at 0x7f4f1cf0b128>

Once loaded, each function in the ABI can be accessed as an attribute of the
``CDLL`` object. For example:

.. code-block:: python

   >>> lib_example.make_udf
   <_FuncPtr object at 0x7f4f1d15f688>
   >>> lib_example.foo
   <_FuncPtr object at 0x7f4f1d15f750>

See the ``ctypes`` `documentation`_ for more information on making
foreign calls.

.. _documentation: https://docs.python.org/3/library/ctypes.html

*****
Usage
*****

Each user defined type can be described by subclasses of
``ctypes.Structure``, which are used to describe the fields in
a C ``struct``:

.. literalinclude:: ../../python/check_ctypes.py
   :language: python
   :lines: 32-54

Note in particular that NumPy provides the ``numpy.ctypeslib`` module
for ``ctypes``\-based interoperability.

To go the other direction, i.e. from a NumPy ``array`` to a ``double*``
pointer:

.. literalinclude:: ../../python/check_ctypes.py
   :language: python
   :lines: 57-58

In order to call :c:func:`udf_ptr`, a ``UserDefined`` instance is
created and an opaque ``intptr_t`` value is passed by reference:

.. literalinclude:: ../../python/check_ctypes.py
   :language: python
   :dedent: 4
   :lines: 132-133

In order to convert the pointer to the data held in the ``ctypes.Structure``
instance to an ``intptr_t``, the ``UserDefined*`` pointer is first converted
to a ``void*`` pointer:

.. literalinclude:: ../../python/check_ctypes.py
   :language: python
   :lines: 71-76

To call ``view_knob()``, the mangled name must be used:

.. literalinclude:: ../../python/check_ctypes.py
   :language: python
   :lines: 79,82

******
Output
******

.. code-block:: console

   $ python python/check_ctypes.py
   ------------------------------------------------------------
   quux = foo(c_double(1.0), c_double(16.0)) = c_double(61.0)
   ------------------------------------------------------------
   quuz = make_udf(c_double(1.25), c_double(5.0), c_int(1337))
        = UserDefined(buzz=1.25, broken=5.0, how_many=1337)
   needsfree(quuz) = True
   address(quuz) = 139757150344968  # 0x7f1bbf4d1708
   *address(quuz) =
       UserDefined(buzz=1.25, broken=5.0, how_many=1337)
   ------------------------------------------------------------
   val =
   [[ 3.    4.5 ]
    [ 1.    1.25]
    [ 9.    0.  ]
    [-1.    4.  ]]
   two_val = foo_array(c_int(4), val)
   two_val =
   [[ 6.   9. ]
    [ 2.   2.5]
    [18.   0. ]
    [-2.   8. ]]
   ------------------------------------------------------------
   ptr_as_int = address(made_it)  # intptr_t / ssize_t / long
   ptr_as_int = c_long(139757150344992)  # 0x7f1bbf4d1720
   udf_ptr(ptr_as_int)  # Set memory in ``made_it``
   made_it = UserDefined(buzz=3.125, broken=-10.5, how_many=101)
   needsfree(made_it) = True
   *ptr_as_int =
       UserDefined(buzz=3.125, broken=-10.5, how_many=101)
   ------------------------------------------------------------
   contained =
   [[0. 4.]
    [1. 9.]
    [1. 2.]
    [3. 1.]]
   container = make_container(contained)
   container.data =
   [[0. 4.]
    [1. 9.]
    [1. 2.]
    [3. 1.]]
   address(contained)      = 43439344  # 0x296d4f0
   address(container)      = 139757150084784  # 0x7f1bbf491eb0
   address(container.data) = 139757150084784  # 0x7f1bbf491eb0
   ------------------------------------------------------------
   just_print()
    ======== BEGIN FORTRAN ========
    just_print() was called
    ========  END  FORTRAN ========
   ------------------------------------------------------------
   view_knob() = 1337
   turn_knob(c_int(42))
   view_knob() = 42

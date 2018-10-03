########
``f2py``
########

Rather than calling into a shared library via ``ctypes`` or
``cffi``, the ``f2py`` `tool`_ can be used to to wrap Fortran
interfaces in Python functions. It does this by generating
a custom CPython `C extension`_ and compiling it with a
Fortran shared library.

.. _tool: https://docs.scipy.org/doc/numpy/f2py/usage.html
.. _C extension: https://docs.python.org/3.6/extending/extending.html

``f2py`` has many limitations, chief of which is absence of support
for user defined types or derived types (equivalent of a C ``struct``).
The examples below demonstrate a few ways of getting around these
limitations, including manual conversion of a custom typed variable
to raw bytes.

*****
Usage
*****

First, the ``f2py`` tool must be used to create an extension module:

.. code-block:: console

   $ f2py \
   >   --verbose \
   >   -c \
   >   --opt='-O3' \
   >   -m example \
   >   fortran/example.f90 \
   >   skip: make_container view_knob
   $ ls *.so
   example.cpython-37m-x86_64-linux-gnu.so*

As we can see, this interacts directly with the Fortran source rather than
with an object file or a shared library.

Inside the ``example.so`` module we've created, the only attribute is
``example``, which represents the Fortran module in ``example.f90``:

.. code-block:: python

   >>> import example
   >>> example
   <module 'example' from '.../example.cpython-37m-x86_64-linux-gnu.so'>
   >>> [name for name in dir(example) if not name.startswith("__")]
   ['example']
   >>> example.example
   <fortran object>

It is within this wrapped Fortran module that our actual routines live:

.. code-block:: python

   >>> example_ns = example.example
   >>> for name in dir(example_ns):
   ...     if not name.startswith("__"):
   ...         print(name)
   ...
   foo
   foo_array
   foo_by_ref
   just_print
   make_udf
   turn_knob
   udf_ptr

The first task we'll accomplish is to call :c:func:`foo` and
``foo_by_ref()``:

.. literalinclude:: ../../f2py/check_f2py.py
   :language: python
   :dedent: 4
   :lines: 39-49

As can be seen in the output below. Calling by reference results in the
correct answer while calling by value (:c:func:`foo`) does not work correctly
with ``f2py``.

Next, we invoke the :c:func:`make_udf` routine to "smuggle" out a
:c:type:`UserDefined` value as raw bytes:

.. literalinclude:: ../../f2py/check_f2py.py
   :language: python
   :dedent: 4
   :lines: 52-59

In particular, this uses the ``np_to_udf`` helper to convert those bytes into
a :c:type:`UserDefined` object as defined in :doc:`ctypes`:

.. literalinclude:: ../../f2py/check_f2py.py
   :language: python
   :lines: 21,23-24

For :c:func:`udf_ptr`, the other routine which deals with a user defined type,
we use the ``prepare_udf`` helper from :doc:`ctypes`. This allocates the memory
for the :c:type:`UserDefined` value in Python and then passes a ``void*``
pointer (as an integer) to the Fortran routine:

.. literalinclude:: ../../f2py/check_f2py.py
   :language: python
   :dedent: 4
   :lines: 68-73

Since ``f2py`` is included with NumPy, it has nicer support for NumPy arrays
than either ``ctypes`` or ``cffi``. This means we can call :c:func:`foo_array`
directly with a NumPy array:

.. literalinclude:: ../../f2py/check_f2py.py
   :language: python
   :dedent: 4
   :lines: 62-65

Finally, we call :c:func:`just_print` to mix Python and Fortran usage of
``STDOUT``:

.. literalinclude:: ../../f2py/check_f2py.py
   :language: python
   :dedent: 4
   :lines: 76-78

******
Output
******

.. code-block:: console

   $ python f2py/check_f2py.py
   ------------------------------------------------------------
   example: <module 'example' from '.../f2py/example...so'>
   dir(example.example): foo, foo_array, foo_by_ref, just_print, make_udf, udf_ptr
   ------------------------------------------------------------
   foo       (1.0, 16.0) = 0.0
   foo_by_ref(1.0, 16.0) = 61.0
   ------------------------------------------------------------
   quuz = make_udf(1.25, 5.0, 1337)
        = UserDefined(buzz=1.25, broken=5.0, how_many=1337)
   ------------------------------------------------------------
   val =
   [[ 3.    4.5 ]
    [ 1.    1.25]
    [ 9.    0.  ]
    [-1.    4.  ]]
   two_val = foo_array(val)
   two_val =
   [[  6.    9. ]
    [  2.    2.5]
    [ 18.    0. ]
    [ -2.    8. ]]
   ------------------------------------------------------------
   ptr_as_int = address(made_it)  # intptr_t / ssize_t / long
   ptr_as_int = 139859191412464  # 0x7f33816c36f0
   udf_ptr(ptr_as_int)  # Set memory in ``made_it``
   made_it = UserDefined(buzz=3.125, broken=-10.5, how_many=101)
   ------------------------------------------------------------
   just_print()
    ======== BEGIN FORTRAN ========
    just_print() was called
    ========  END  FORTRAN ========

******************
What is Happening?
******************

``f2py`` actually generates a wrapped ``{modname}module.c`` file (so in our
case ``examplemodule.c``) and utilizes a ``fortranobject`` C library to create
CPython C extensions:

.. code-block:: python

   >>> import os
   >>> import numpy.f2py
   >>>
   >>> f2py_dir = os.path.dirname(numpy.f2py.__file__)
   >>> f2py_dir
   '.../lib/python3.7/site-packages/numpy/f2py'
   >>> os.listdir(os.path.join(f2py_dir, 'src'))
   ['fortranobject.c', 'fortranobject.h']

It uses a C compiler with flags determined by ``distutils`` to
link against NumPy and Python headers when compiling ``{modname}module.c``
and ``fortranobject.c`` and uses a Fortran compiler for ``{modname}.f90``.
Then it uses the Fortran compiler as linker:

.. code-block:: console

   $ gfortran \
   >   -Wall \
   >   -g \
   >   -shared \
   >   ${TEMPDIR}/.../{modname}module.o \
   >   ${TEMPDIR}/.../fortranobject.o \
   >   ${TEMPDIR}/{modname}.o \
   >   -lgfortran \
   >   -o \
   >   ./{modname}.so

When trying to convert a Fortran subroutine to Python via ``f2py``, a
problem occurs if the subroutine uses a user defined type. For example, if
we tried to use the :c:func:`make_container` routine:

.. code-block:: console

   $ f2py \
   >   --verbose \
   >   -c \
   >   --opt='-O3' \
   >   -m example \
   >   fortran/example.f90 \
   >   only: make_container
   ...
   Building modules...
           Building module "example"...
                   Constructing F90 module support for "example"...
   Skipping type unknown_type
   Skipping type unknown_type
                           Constructing wrapper function "example.make_container"...
   getctype: No C-type found in "{'typespec': 'type', 'typename': 'datacontainer', 'attrspec': [], 'intent': ['out']}", assuming void.
   getctype: No C-type found in "{'typespec': 'type', 'typename': 'datacontainer', 'attrspec': [], 'intent': ['out']}", assuming void.
   getctype: No C-type found in "{'typespec': 'type', 'typename': 'datacontainer', 'attrspec': [], 'intent': ['out']}", assuming void.
   Traceback (most recent call last):
   ...
     File ".../numpy/f2py/capi_maps.py", line 412,in getpydocsign
       sig = '%s : %s %s%s' % (a, opt, c2py_map[ctype], init)
   KeyError: 'void'

This is because :c:func:`make_container` returns the :c:type:`DataContainer`
user defined type.

**********
References
**********

- (Lack of) `support`_ for user defined types in ``f2py``
- The ``f90wrap`` `interface generator`_ adds support for user defined
  types to ``f2py``. However, the author of this document has no experience
  with ``f90wrap``.

.. _support: https://mail.scipy.org/pipermail/scipy-user/2008-December/018881.html
.. _interface generator: https://github.com/jameskermode/f90wrap

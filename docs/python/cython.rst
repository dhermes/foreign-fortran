######
Cython
######

`Cython`_ is a mature and heavily used extension of the Python
programming language. It allows writing optionally typed Python code,
implementing part of a Python module completely in C and many other
performance benefits.

.. _Cython: https://cython.readthedocs.io/

It is **very** mature. For example, a ``.pyx`` Cython file can be compiled
both to a standard CPython `C extension`_ as well as providing
`basic support`_ for the `PyPy`_ emulation layer ``cpyext``.

.. _C extension: https://docs.python.org/3/extending/extending.html
.. _basic support: https://cython.readthedocs.io/en/latest/src/userguide/pypy.html
.. _PyPy: https://pypy.org/

*****
Usage
*****

The ABI for the Fortran module is provided in a Cython declaration
``example_fortran.pxd`` which we will reference throughout:

.. literalinclude:: ../../cython/package/example/fast.pyx
   :language: cython
   :lines: 8

Using this, values can be passed by value into :c:func:`foo` using typical
C pass by value convention:

.. literalinclude:: ../../cython/package/example/fast.pyx
   :language: cython
   :lines: 11-14

For the :c:type:`UserDefined` Fortran type, the ``example_fortran.pxd``
defines a matching ``struct``:

.. literalinclude:: ../../cython/package/example/example_fortran.pxd
   :language: cython
   :dedent: 4
   :lines: 4-7

This can then be used for :c:func:`make_udf`:

.. literalinclude:: ../../cython/package/example/fast.pyx
   :language: cython
   :lines: 17-20

and for :c:func:`udf_ptr`:

.. literalinclude:: ../../cython/package/example/fast.pyx
   :language: cython
   :lines: 2,39-43

In either case, the :c:type:`UserDefined` value is created by each function
(i.e. from Python, not from Fortran) and then a pointer to that memory is
passed along to the relevant Fortran routine:

.. literalinclude:: ../../cython/package/example/fast.pyx
   :language: cython
   :dedent: 4
   :lines: 40

When calling :c:func:`foo_array` we allow NumPy arrays and Cython allows
us to specify that the array is 2D and Fortran-contiguous. We also turn
off bounds checking since the only array indices used are ``0``:

.. literalinclude:: ../../cython/package/example/fast.pyx
   :language: cython
   :lines: 23-36

Calling :c:func:`just_print` simply requires wrapping a C call in a Python
function (i.e. ``def`` not ``cdef``):

.. literalinclude:: ../../cython/package/example/fast.pyx
   :language: cython
   :lines: 46-47

When invoking ``view_knob()``, we must do a little extra work. The ``f2py``
parser has a bug when a Fortran ``function`` (vs. a ``subroutine``) has
``bind(c, name=...)``. In order to allow ``f2py`` to wrap ``example.f90``, we
don't specify the non-mangled name in the ABI, hence must reference the mangled
name from the object file:

.. literalinclude:: ../../cython/package/example/example_fortran.pxd
   :language: cython
   :dedent: 4
   :lines: 21

Luckily the mangled name can be aliased in the ``.pxd`` declaration and then
calling ``view_knob()`` in Cython is straightforward:

.. literalinclude:: ../../cython/package/example/fast.pyx
   :language: cython
   :lines: 50-51

Similarly :c:func:`turn_knob` is also straightforward:

.. literalinclude:: ../../cython/package/example/fast.pyx
   :language: cython
   :lines: 54-55

******
Output
******

.. code-block:: console

   $ python cython/check_cython.py
   ------------------------------------------------------------
   quux = foo(1.0, 16.0) = 61.0
   ------------------------------------------------------------
   quuz = make_udf(1.25, 5.0, 1337)
        = {'buzz': 1.25, 'broken': 5.0, 'how_many': 1337}
   ------------------------------------------------------------
   val =
   [[ 3.    4.5 ]
    [ 1.    1.25]
    [ 9.    0.  ]
    [-1.    4.  ]]
   two_val = foo_array(val)
   two_val =
   [[ 6.   9. ]
    [ 2.   2.5]
    [18.   0. ]
    [-2.   8. ]]
   ------------------------------------------------------------
   made_it = udf_ptr()
           = {'buzz': 3.125, 'broken': -10.5, 'how_many': 101}
   ------------------------------------------------------------
   just_print()
    ======== BEGIN FORTRAN ========
    just_print() was called
    ========  END  FORTRAN ========
   ------------------------------------------------------------
   example.get_include() =
   .../foreign-fortran/cython/venv/lib/python.../site-packages/example/include
   ------------------------------------------------------------
   view_knob() = 1337
   turn_knob(42)
   view_knob() = 42

*****************************
``sdist`` and installed files
*****************************

On a standard CPython install on Linux, a source dist (``sdist``)
contains the following:

.. code-block:: rest

   .
   ├── example
   │   ├── example.f90
   │   ├── example_fortran.pxd
   │   ├── fast.c
   │   ├── include
   │   │   └── example.h
   │   └── __init__.py
   ├── example.egg-info
   │   ├── dependency_links.txt
   │   ├── PKG-INFO
   │   ├── SOURCES.txt
   │   └── top_level.txt
   ├── MANIFEST.in
   ├── PKG-INFO
   ├── setup.cfg
   └── setup.py

   3 directories, 13 files

Once this gets installed, the following files are present:

.. code-block:: rest

   .
   ├── example_fortran.pxd
   ├── fast.cpython-37m-x86_64-linux-gnu.so
   ├── include
   │   └── example.h
   ├── __init__.py
   ├── lib
   │   └── libexample.a
   └── __pycache__
       └── __init__.cpython-37.pyc

   3 directories, 6 files

****************************
``cimport``-ing this library
****************************

This library provides an ``example/example_fortran.pxd`` declaration file
that can be used to ``cimport`` the library without having to worry about
the Python layer:

.. code-block:: cython

   cimport example.example_fortran

In this case, the library referenced in ``example_fortran.pxd``
is made available in the ``example`` package:

.. code-block:: python

   >>> import os
   >>> import example
   >>>
   >>> include_dir = example.get_include()
   >>> include_dir
   '.../foreign-fortran/cython/venv/lib/python.../site-packages/example/include'
   >>> os.listdir(include_dir)
   ['example.h']
   >>>
   >>> lib_dir = example.get_lib()
   >>> lib_dir
   '.../foreign-fortran/cython/venv/lib/python.../site-packages/example/lib'
   >>> os.listdir(lib_dir)
   ['libexample.a']

See ``cython/use_cimport/setup.py`` for an example of how to wrap:

.. code-block:: python

   >>> wrapper.morp()
    ======== BEGIN FORTRAN ========
    just_print() was called
    ========  END  FORTRAN ========
   >>> example.foo(1.5, 2.5)
   10.875
   >>> wrapper.triple_foo(1.5, 2.5)
   32.625

******
Gotcha
******

If ``libraries=['gfortran']`` is not specified in ``setup.py`` when
building the CPython C extension module (``example.so``), then the print
statements in :c:func:`just_print` (as defined in in ``example.f90``) cause

.. code-block:: console

   $ IGNORE_LIBRARIES=true python setup.py build_ext --inplace
   running build_ext
   ...
   $ python -c 'import example'
   Traceback (most recent call last):
     File "<string>", line 1, in <module>
     File ".../cython/package/example/__init__.py", line 5, in <module>
       from example import fast
   ImportError: .../cython/package/example/fast...so: undefined symbol: _gfortran_transfer_character_write

**********
References
**********

- Decently `helpful article`_ and `pre-article`_ to that one about
  using Cython to wrap Fortran. But this article fails to point out
  its approach can leave out some symbols (e.g. the ``check_cython``
  example when ``libgfortran`` isn't included)
- Description on the uber-useful ``fortran90.org`` on
  `how to interface with C`_

.. _helpful article: https://maurow.bitbucket.io/notes/calling_fortran_from_python.html
.. _pre-article: https://maurow.bitbucket.io/notes/calling_fortran_from_c.html
.. _how to interface with C: http://www.fortran90.org/src/best-practices.html#interfacing-with-c

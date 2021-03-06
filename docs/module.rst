##############
Shared Library
##############

We define a simple module that contains a particular subset
of Fortran features. Many of them are exported with unmangled
names (via ``bind(c)``) so the ABI can be used in a predictable way
independent of the compiler or platform.

****************
Public Interface
****************

.. c:var:: int KNOB

   The first public symbol is a mutable global:

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 12

   :c:data:`KNOB` does not have a bound name (i.e. it may be mangled)
   and it is expected to be accessed via a public getter and setter.

.. c:function:: void turn_knob(int *new_value)

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 100-114

   **C Signature:**

   .. literalinclude:: ../c/example.h
      :language: c
      :lines: 24

   As noted in the remark, the ``view_knob()`` getter also does not have a
   bound name because of the way a ``function`` (vs. a ``subroutine``) is
   parsed by ``f2py`` (an `issue`_ has been filed).

   .. _issue: https://github.com/numpy/numpy/issues/9693

In addition to a mutable global, there are two user defined types
exposed and unmangled, hence each acts as a C ``struct``.

.. c:type:: UserDefined

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 14,16-19

   **C Signature:**

   .. literalinclude:: ../c/example.h
      :language: c
      :lines: 8-12

   .. c:var:: double buzz
   .. c:var:: double broken
   .. c:var:: int how_many

.. c:type:: DataContainer

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 21-23

   **C Signature:**

   .. literalinclude:: ../c/example.h
      :language: c
      :lines: 14

   .. c:var:: double[8] data

.. c:function:: void foo(double bar, double baz, double *quux)

   The first subroutine exported by the public interface is an implementation
   of ``f(x, y) = x + 3.75 y``.

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 27-33

   **C Signature:**

   .. literalinclude:: ../c/example.h
      :language: c
      :lines: 16

   It accepts the inputs by value. Since pass-by-reference is the default
   behavior, an equivalent method is provided (though not as part of the
   unmangled ABI):

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 35-41

.. c:function:: void foo_array(int *size, double *val, double *two_val)

   Next, we define a method that accepts a variable size array and places
   twice the values of that array in the return value:

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 43-50

   **C Signature:**

   .. literalinclude:: ../c/example.h
      :language: c
      :lines: 18

.. c:function:: void make_udf(double *buzz, \
                              double *broken, \
                              int *how_many, \
                              UserDefined *quuz)

   The next subroutine creates an instance of the :c:type:`UserDefined` data type,
   but **smuggles** the result out as raw bytes. The total size is
   ``size(buzz) + size(broken) + size(how_many) = 2 c_double + c_int``. This
   is 20 bytes on most platforms, but as a struct it gets padded to 24 due to
   word size.

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 52-66

   **C Signature:**

   .. literalinclude:: ../c/example.h
      :language: c
      :lines: 19

   This concept of "data smuggling" is necessary for the use of user defined
   types with ``f2py``, since it has no support for them.

.. c:function:: void udf_ptr(intptr_t *ptr_as_int)

   A related way to smuggle data for use with ``f2py`` is to allocate
   memory for the struct and then pass a pointer to that memory
   as an opaque integer. Once this is done, the Fortran subroutine
   can convert the integer into a Fortran ``pointer`` and then
   write to the memory location owned by the foreign caller:

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 68-81

   **C Signature:**

   .. literalinclude:: ../c/example.h
      :language: c
      :lines: 20

   This approach is problematic because it is so brittle. The memory
   must be handled by the caller rather than by Fortran directly.
   If the subroutine were responsible for the memory, the object would
   likely be allocated on the stack and the memory location re-used by
   subsequent calls to the subroutine.

.. c:function:: void make_container(double *contained, \
                                    DataContainer *container)

   The next subroutine takes an array as input and sets the ``data``
   attribute of a returned :c:type:`DataContainer` instance as the input.
   This acts as a check that the operation happens as a data copy rather than
   a reference copy.

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 83-90

   **C Signature:**

   .. literalinclude:: ../c/example.h
      :language: c
      :lines: 21

.. c:function:: void just_print(void)

   The :c:func:`just_print` subroutine simply prints characters to the screen.
   However, printing requires ``libgfortran``, which slightly complicates
   foreign usage.

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 92-98

   **C Signature:**

   .. literalinclude:: ../c/example.h
      :language: c
      :lines: 22

.. _object-file:

***********
Object File
***********

For some foreign usage of ``example``, we'll directly use a compiled
object file. To create ``example.o``:

.. code-block:: console

   $ gfortran \
   >   -J fortran/ \
   >   -c fortran/example.f90 \
   >   -o fortran/example.o

.. _shared-object:

*************
Shared Object
*************

It's more common for foreign usage of native code to be done via a
shared object file:

.. code-block:: console

   $ gfortran \
   >   -shared -fPIC \
   >   -J fortran/ \
   >   fortran/example.f90 \
   >   -o fortran/example.so

Here, we manually build a "position independent" shared library in the
same directory as the source. However, in many cases, native code comes
with an installer that puts the library in a standard place, e.g. a
symlink to ``libatlas`` can be found in ``/usr/lib/libatlas.so``. Shared
object files are typically named ``lib{pkg}.so`` so that they can be
included by the compiler with ``-l{pkg}``. The compiler uses a default list of
"search directories" when finding such shared libraries.

**********
References
**********

* `Examples`_ of user-defined types
* StackOverflow `question`_ about user-defined types
* The ``sphinx-fortran`` `project`_ was started to provide ``autodoc``
  capabilities for Fortran libraries, but it is not actively maintained
  (as of this writing, August 2018)
* The `AutoAPI`_ redesign of ``autodoc`` will hopefully mature into a
  capable way of documenting Fortran code (and code from other languages)
  using Sphinx
* The `FORD`_ (FORtran Documentation) project is a modern way to generate
  documentation for Fortran code, though it is "Yet Another" documentation
  generator (`example documentation`_)
* The ``breathe`` project / library seeks to be a `bridge`_ Python XML-based
  doxygen and Sphinx, though in practice the formatting of doxygen produced
  documentation is not in line with typical Sphinx documentation

.. _Examples: http://www.mathcs.emory.edu/~cheung/Courses/561/Syllabus/6-Fortran/struct.html
.. _question: https://stackoverflow.com/q/8557244
.. _project: https://sphinx-fortran.readthedocs.io/en/latest/
.. _AutoAPI: http://sphinx-autoapi.readthedocs.io/en/latest/
.. _FORD: https://github.com/Fortran-FOSS-Programmers/ford
.. _example documentation: https://jacobwilliams.github.io/json-fortran/
.. _bridge: https://github.com/michaeljones/breathe

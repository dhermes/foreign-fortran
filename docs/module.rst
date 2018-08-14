##############
Shared Library
##############

We define a simple module that contains a particular subset
of Fortran features. Many of them are exported with unmangled
names (via ``bind(c)``) so the ABI can be used in a predictable way
independent of the compiler or platform.

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
      :lines: 28

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
      :lines: 14-16

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
      :lines: 18

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
      :lines: 20

.. c:function:: void make_udf(double *buzz, \
                              double *broken, \
                              int *how_many, \
                              UserDefined *quuz)

   The next subroutine creates an instance of the :c:type:`UserDefined` data type,
   but **smuggles** the result out as raw bytes. The total size is
   ``size(buzz) + size(broken) + size(how_many) = 2 c_double + c_int``. This
   is 24 bytes on most platforms.

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 52-66

   **C Signature:**

   .. literalinclude:: ../c/example.h
      :language: c
      :lines: 21-23

   This concept of "data smuggling" is necessary for the use of user defined
   types with ``f2py``, since it has no support for them.

.. c:function:: void udf_ptr(intptr_t *ptr_as_int)

   A related way to smuggle data for use with ``f2py`` is to cast a pointer
   to the user defined type into an integer and return the integer:

   **Fortran Implementation:**

   .. literalinclude:: ../fortran/example.f90
      :language: fortran
      :dedent: 2
      :lines: 68-81

   **C Signature:**

   .. literalinclude:: ../c/example.h
      :language: c
      :lines: 24

   This approach is problematic because it forces the Fortran function
   to handle allocation of memory for the object. If instead the caller
   were responsible for the memory, then cleanup would be handled in the
   correct place, but instead the object may be allocated on the stack
   and the memory location re-used by subsequent calls to the subroutine.

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
      :lines: 25

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
      :lines: 26

.. _build:

*****
Build
*****

For some foreign usage of ``example``, we'll directly use a compiled
object file. To create ``example.o``:

.. code-block:: console

   $ gfortran \
   >   -J fortran/ \
   >   -c fortran/example.f90 \
   >   -o fortran/example.o

**********
References
**********

* `Examples`_ of user-defined types
* StackOverflow `question`_ about user-defined types
* The ``sphinx-fortran`` `project`_ was started to provide ``autodoc``
  capabilities for Fortran libraries, but it is not actively maintained
  (as of this writing, August 2018)

.. _Examples: http://www.mathcs.emory.edu/~cheung/Courses/561/Syllabus/6-Fortran/struct.html
.. _question: https://stackoverflow.com/q/8557244
.. _project: https://sphinx-fortran.readthedocs.io/en/latest/

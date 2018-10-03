######
Python
######

There are several ways to make foreign calls from within a Python program,
each with it's own pros and cons. Of the methods listed, only :doc:`f2py`
is specific to Fortran. The rest can be used for any native code that can be
built into the artifacts needed for that particular method.

.. toctree::
   :titlesonly:

   ctypes
   cffi
   f2py
   cython

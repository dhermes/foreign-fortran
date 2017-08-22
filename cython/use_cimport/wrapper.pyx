cimport example.example_fortran


def morp():
    example.example_fortran.just_print()


def triple_foo(double bar, double baz):
    cdef double quux
    example.example_fortran.foo(bar, baz, &quux)
    return 3.0 * quux

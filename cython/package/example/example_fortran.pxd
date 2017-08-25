from libc.stdint cimport intptr_t

cdef extern from "example.h":
    ctypedef struct UserDefined:
        double buzz
        double broken
        int how_many

    ctypedef struct DataContainer:
        double data[8]

    void foo(double bar, double baz, double *quux)
    void __example_MOD_foo_by_ref(double *bar, double *baz, double *quux)
    void foo_array(int *size, double *val, double *two_val)
    void make_udf(double *buzz, double *broken, int *how_many, UserDefined *quuz)
    void udf_ptr(intptr_t *ptr_as_int)
    void make_container(double *contained, DataContainer *container)
    void just_print()

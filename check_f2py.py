import numpy as np

import fortran_example
from check_ctypes import prepare_udf


MSG_FOO_ARRAY = """\
val =
{1}
two_val = fortran_example.example.foo_array(val, {0})
two_val =
{2}"""
UDF_PTR_TEMPLATE = """\
ptr_as_int = address(made_it) -> long
ptr_as_int = {}
udf_ptr(ptr_as_int)  # Set memory in ``made_it``
made_it = {}"""
SEPARATOR = '-' * 60


def main():
    print('fortran_example: {}'.format(fortran_example))
    example_ns = fortran_example.example
    print('dir(fortran_example.example): {}'.format(dir(example_ns)))

    print(SEPARATOR)
    bar = 1.0
    baz = 16.0
    msg_foo = 'fortran_example.example.foo      ({}, {}) = {}'.format(
        bar, baz, example_ns.foo(bar, baz))
    print(msg_foo)
    msg_foo_not_c = 'fortran_example.example.foo_not_c({}, {}) = {}'.format(
        bar, baz, example_ns.foo_not_c(bar, baz))
    print(msg_foo_not_c)

    print(SEPARATOR)
    val = np.asfortranarray([
        [ 3.0, 4.5 ],
        [ 1.0, 1.25],
        [ 9.0, 0.0 ],
        [-1.0, 4.0 ],
    ])
    size, _ = val.shape
    two_val = example_ns.foo_array(val)
    print(MSG_FOO_ARRAY.format(size, val, two_val))

    print(SEPARATOR)
    made_it, ptr_as_int = prepare_udf()
    ptr_as_int = ptr_as_int.value
    example_ns.udf_ptr(ptr_as_int)
    msg = UDF_PTR_TEMPLATE.format(ptr_as_int, made_it)
    print(msg)


if __name__ == '__main__':
    main()

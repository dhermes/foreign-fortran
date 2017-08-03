from __future__ import print_function

import numpy as np

from check_ctypes import MAKE_UDF_TEMPLATE
from check_ctypes import prepare_udf
from check_ctypes import SEPARATOR
from check_ctypes import UDF_PTR_TEMPLATE
from check_ctypes import UserDefined
import fortran_example


MSG_FOO_ARRAY = """\
val =
{}
two_val = foo_array(val)
two_val =
{}"""


def np_to_udf(arr):
    assert arr.dtype == np.dtype('S1')
    address = arr.ctypes.data
    return UserDefined.from_address(address)


def main():
    print(SEPARATOR)
    print('fortran_example: {}'.format(fortran_example))
    example_ns = fortran_example.example
    print('dir(fortran_example.example): {}'.format(dir(example_ns)))

    print(SEPARATOR)
    # foo()
    bar = 1.0
    baz = 16.0
    msg_foo = 'foo       ({}, {}) = {}'.format(
        bar, baz, example_ns.foo(bar, baz))
    print(msg_foo)
    msg_foo_by_ref = 'foo_by_ref({}, {}) = {}'.format(
        bar, baz, example_ns.foo_by_ref(bar, baz))
    print(msg_foo_by_ref)

    print(SEPARATOR)
    # make_udf()
    buzz = 1.25
    broken = 5.0
    how_many = 1337
    quuz_as_bytes = example_ns.make_udf(buzz, broken, how_many)
    quuz = np_to_udf(quuz_as_bytes)
    msg = MAKE_UDF_TEMPLATE.format(buzz, broken, how_many, quuz)
    print(msg, end='')

    print(SEPARATOR)
    # foo_array()
    val = np.asfortranarray([
        [ 3.0, 4.5 ],
        [ 1.0, 1.25],
        [ 9.0, 0.0 ],
        [-1.0, 4.0 ],
    ])
    two_val = example_ns.foo_array(val)
    print(MSG_FOO_ARRAY.format(val, two_val))

    print(SEPARATOR)
    # udf_ptr()
    made_it, ptr_as_int = prepare_udf()
    ptr_as_int = ptr_as_int.value
    example_ns.udf_ptr(ptr_as_int)
    msg = UDF_PTR_TEMPLATE.format(ptr_as_int, ptr_as_int, made_it)
    print(msg, end='')

    print(SEPARATOR)
    # just_print()
    print('just_print()')
    example_ns.just_print()


if __name__ == '__main__':
    main()

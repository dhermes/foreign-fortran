import numpy as np

import fortran_example


MSG_FOO_ARRAY = """\
fortran_example.example.foo_array(
    {},
    {},
) =
{}
"""


def main():
    print('fortran_example: {}'.format(fortran_example))
    if fortran_example is None:
        return

    example = fortran_example.example
    print('fortran_example.example: {}'.format(example))
    print('dir(fortran_example.example): {}'.format(dir(example)))
    bar = 1.0
    baz = 16.0
    msg_foo = 'fortran_example.example.foo      ({}, {}) = {}'.format(
        bar, baz, fortran_example.example.foo(bar, baz))
    print(msg_foo)
    msg_foo_not_c = 'fortran_example.example.foo_not_c({}, {}) = {}'.format(
        bar, baz, fortran_example.example.foo_not_c(bar, baz))
    print(msg_foo_not_c)

    val = np.asfortranarray([
        [ 3.0, 4.5 ],
        [ 1.0, 1.25],
        [ 9.0, 0.0 ],
        [-1.0, 4.0 ],
    ])
    size, _ = val.shape
    two_val = fortran_example.example.foo_array(val)
    print(MSG_FOO_ARRAY.format(size, val, two_val))


if __name__ == '__main__':
    main()

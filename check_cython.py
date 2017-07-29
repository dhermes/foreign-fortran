import numpy as np

from check_ctypes import SEPARATOR
import cy_example


def main():
    # foo()
    bar = 1.0
    baz = 16.0
    quux = cy_example.foo(bar, baz)
    print('quux = foo({}, {}) = {}'.format(bar, baz, quux))

    print(SEPARATOR)
    # make_udf()
    buzz = 1.25
    broken = 5.0
    how_many = 1337
    quuz = cy_example.make_udf(buzz, broken, how_many)
    msg = 'quuz = make_udf({}, {}, {})\n     = {}'.format(
        buzz, broken, how_many, quuz)
    print(msg)

    print(SEPARATOR)
    # foo_array()
    val = np.asfortranarray([
        [ 3.0, 4.5 ],
        [ 1.0, 1.25],
        [ 9.0, 0.0 ],
        [-1.0, 4.0 ],
    ])
    two_val = cy_example.foo_array(val)
    print('val =\n{}'.format(val))
    print('two_val = foo_array(val)')
    print('two_val =\n{}'.format(two_val))

    print(SEPARATOR)
    # udf_ptr()
    made_it = cy_example.udf_ptr()
    print('made_it = udf_ptr()\n        = {}'.format(made_it))


if __name__ == '__main__':
    main()

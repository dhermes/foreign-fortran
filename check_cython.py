import numpy as np

import cy_example


def main():
    bar = 1.0
    baz = 16.0
    quux = cy_example.foo_(bar, baz)
    print('quux = foo({}, {}) = {}'.format(bar, baz, quux))

    buzz = 1.25
    broken = 5.0
    how_many = 1337
    quuz = cy_example.make_udf_(buzz, broken, how_many)
    msg = 'quuz = make_udf_({}, {}, {}) = {}'.format(
        buzz, broken, how_many, quuz)
    print(msg)

    val = np.asfortranarray([
        [ 3.0, 4.5 ],
        [ 1.0, 1.25],
        [ 9.0, 0.0 ],
        [-1.0, 4.0 ],
    ])
    two_val = cy_example.foo_array_(val)
    print('val =\n{}'.format(val))
    print('two_val = foo_array_(val)')
    print('two_val =\n{}'.format(two_val))


if __name__ == '__main__':
    main()

import numpy as np

import cy_example


def main():
    bar = 1.0
    baz = 16.0
    quux = cy_example.foo_(bar, baz)
    print('quux = foo({}, {}) = {}'.format(bar, baz, quux))

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

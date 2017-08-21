from __future__ import print_function

import numpy as np

from check_ctypes import MAKE_UDF_TEMPLATE
from check_ctypes import SEPARATOR
import example


def main():
    print(SEPARATOR)
    # foo()
    bar = 1.0
    baz = 16.0
    quux = example.foo(bar, baz)
    print('quux = foo({}, {}) = {}'.format(bar, baz, quux))

    print(SEPARATOR)
    # make_udf()
    buzz = 1.25
    broken = 5.0
    how_many = 1337
    quuz = example.make_udf(buzz, broken, how_many)
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
    two_val = example.foo_array(val)
    print('val =\n{}'.format(val))
    print('two_val = foo_array(val)')
    print('two_val =\n{}'.format(two_val))

    print(SEPARATOR)
    # udf_ptr()
    made_it = example.udf_ptr()
    print('made_it = udf_ptr()\n        = {}'.format(made_it))

    print(SEPARATOR)
    # just_print()
    print('just_print()')
    example.just_print()


if __name__ == '__main__':
    main()

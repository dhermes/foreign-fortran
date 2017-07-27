import cy_example


def main():
    bar = 1.0
    baz = 16.0
    quux = cy_example.foo_cython(bar, baz)
    print('quux = foo({}, {}) = {}'.format(bar, baz, quux))


if __name__ == '__main__':
    main()

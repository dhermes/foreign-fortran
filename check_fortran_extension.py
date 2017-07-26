try:
    import fortran_example
except ImportError:
    fortran_example = None


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


if __name__ == '__main__':
    main()

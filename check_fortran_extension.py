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


if __name__ == '__main__':
    main()

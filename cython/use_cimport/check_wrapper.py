import example

import wrapper


def main():
    print(">>> wrapper.morp()")
    return_value = wrapper.morp()
    assert return_value is None

    print(">>> example.foo(1.5, 2.5)")
    result = example.foo(1.5, 2.5)
    print(repr(result))

    print(">>> wrapper.triple_foo(1.5, 2.5)")
    result = wrapper.triple_foo(1.5, 2.5)
    print(repr(result))


if __name__ == "__main__":
    main()

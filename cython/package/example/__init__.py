import os

from example import fast


PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))


foo = fast.foo
make_udf = fast.make_udf
foo_array = fast.foo_array
udf_ptr = fast.udf_ptr
just_print = fast.just_print


def get_include():
    return os.path.join(PACKAGE_ROOT, 'include')

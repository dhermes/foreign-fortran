import Cython.Build
import setuptools

import example


def main():
    extension_keywords = example.get_extension_keywords()
    ext_module = setuptools.Extension(
        "wrapper", ["wrapper.pyx"], **extension_keywords
    )
    setuptools.setup(
        name="cimport-ing example module interface",
        ext_modules=Cython.Build.cythonize([ext_module]),
    )


if __name__ == "__main__":
    main()

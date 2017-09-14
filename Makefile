CC                = gcc
CXX               = g++
FC                = gfortran
PYTHON            = python
F2PY              = f2py
MODULES_DIR       = -J
FORTRAN_LIB       = -lgfortran
FORTRAN_LIB_PATHS = $(shell $(PYTHON) python/fortran_search_path.py)
PYTHON_FULL       = $(shell $(PYTHON) -c 'import sys; print("python{}.{}".format(*sys.version_info[:2]))')
PIC               = -shared -fPIC
EXT_SUFFIX        = $(shell $(PYTHON) -c 'import distutils.sysconfig as DS; print(DS.get_config_var("EXT_SUFFIX") or ".so")')
ROOT_DIR          = $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

all: fortran_example

fortran/example.o fortran/example.mod: fortran/example.f90
	$(FC) \
	  $(MODULES_DIR) fortran/ \
	  -c fortran/example.f90 \
	  -o fortran/example.o

fortran_example: fortran/example.mod fortran/example.o fortran/main.f90
	$(FC) \
	  -o fortran_example \
	  fortran/main.f90 \
	  fortran/example.o

run-fortran: fortran_example
	@./fortran_example

c_example: c/example.c c/example.h fortran/example.o
	$(CC) \
	  -I c/ \
	  -c c/example.c \
	  -o c/example.o
	$(CC) \
	  c/example.o \
	  fortran/example.o \
	  -o c_example \
	  $(FORTRAN_LIB_PATHS) \
	  $(FORTRAN_LIB)
	# OR: gfortran c/example.o fortran/example.o -o c_example

run-c: c_example
	@./c_example

cpp_example: cpp/example.cpp c/example.h fortran/example.o
	$(CXX) \
	  -std=c++11 \
	  -I c/ \
	  -c cpp/example.cpp \
	  -o cpp/example.o
	$(CXX) \
	  cpp/example.o \
	  fortran/example.o \
	  -o cpp_example \
	  $(FORTRAN_LIB_PATHS) \
	  $(FORTRAN_LIB)

run-cpp: cpp_example
	@./cpp_example

python/example.so: fortran/example.f90
	$(FC) \
	  $(PIC) \
	  $(MODULES_DIR) fortran/ \
	  fortran/example.f90 \
	  -o python/example.so

run-ctypes: python/check_ctypes.py python/example.so
	@$(PYTHON) python/check_ctypes.py

run-cffi: python/check_cffi.py python/example.so
	@$(PYTHON) python/check_cffi.py

f2py/example$(EXT_SUFFIX): fortran/example.f90 f2py/.f2py_f2cmap
	cd f2py/ && \
	  $(F2PY) \
	    --verbose \
	    -c \
	    --opt='-O3' \
	    -m example \
	    ../fortran/example.f90 \
	    skip: make_container view_knob

run-f2py: f2py/check_f2py.py f2py/example$(EXT_SUFFIX)
	@$(PYTHON) f2py/check_f2py.py

broken-f2py: fortran/example.f90 f2py/.f2py_f2cmap
	cd f2py/ && \
	  $(F2PY) \
	    --verbose \
	    -c \
	    --opt='-O3' \
	    -m example \
	    ../fortran/example.f90 \
	    only: make_container

cython/package/example/fast.c: cython/package/example/fast.pyx
	cd cython/package/example/ && \
	  cython fast.pyx

cython/venv:
	cd cython && \
	  virtualenv venv && \
	  venv/bin/pip install cffi numpy Cython

cython/venv/lib/$(PYTHON_FULL)/site-packages/example: cython/venv cython/package/setup.py cython/package/example/fast.c c/example.h fortran/example.f90
	# Make sure our copied files are as expected. We use copies
	# instead of symlinks because MANIFEST.in copies the **symlinks**.
	diff --brief c/example.h cython/package/example/include/example.h
	diff --brief fortran/example.f90 cython/package/example/example.f90
	cython/venv/bin/pip install cython/package/

run-cython: cython/venv/lib/$(PYTHON_FULL)/site-packages/example cython/check_cython.py
	@cython/venv/bin/python cython/check_cython.py

broken-cython: cython/package/setup.py cython/package/example/fast.c
	cd cython/package/ && \
	  IGNORE_LIBRARIES=true $(PYTHON) setup.py build_ext --inplace && \
	  $(PYTHON) -c 'import example'

cython/package/dist/example-0.0.1.tar.gz: cython/venv/lib/$(PYTHON_FULL)/site-packages/example
	cd cython/package/ && \
	  ../venv/bin/python setup.py sdist

inspect-cython-sdist: cython/package/dist/example-0.0.1.tar.gz cython/package/MANIFEST.in
	@tar xzf \
	  cython/package/dist/example-0.0.1.tar.gz \
	  -C cython/package/dist/
	@cd cython/package/dist/example-0.0.1 && \
	  tree -a .

inspect-cython-installed: cython/venv/lib/$(PYTHON_FULL)/site-packages/example
	@cd $(shell cython/venv/bin/python \
	  -c 'import example, os; print(os.path.dirname(example.__file__))') && \
	  tree -a .

cython/use_cimport/wrapper$(EXT_SUFFIX): cython/venv/lib/$(PYTHON_FULL)/site-packages/example cython/use_cimport/setup.py
	cd cython/use_cimport && \
	  ../venv/bin/python setup.py build_ext --inplace

wrap-cython: cython/use_cimport/wrapper$(EXT_SUFFIX) cython/use_cimport/check_wrapper.py
	@cd cython/use_cimport && \
	  ../venv/bin/python check_wrapper.py

run-golang: golang/main.go golang/src/example/example.go c/example.h fortran/example.f90
	@CGO_LDFLAGS="$(FORTRAN_LIB_PATHS)" \
	  GOPATH=$(ROOT_DIR)/golang \
	  go run golang/main.go

clean:
	rm -f \
	  c/example.o \
	  c_example \
	  cpp_example \
	  cpp/example.o \
	  cython/check_ctypes.pyc \
	  cython/package/example.mod \
	  cython/package/example/__init__.pyc \
	  cython/package/example/example.o \
	  cython/package/example/fast$(EXT_SUFFIX) \
	  cython/package/MANIFEST \
	  cython/use_cimport/wrapper$(EXT_SUFFIX) \
	  cython/use_cimport/wrapper.c \
	  f2py/check_ctypes.pyc \
	  f2py/example$(EXT_SUFFIX) \
	  fortran/example.mod \
	  fortran/example.o \
	  fortran_example \
	  golang/src/example/example.mod \
	  python/check_ctypes.pyc \
	  python/example.so
	rm -fr \
	  cython/__pycache__/ \
	  cython/package/build/ \
	  cython/package/dist/ \
	  cython/package/example.egg-info/ \
	  cython/package/example/lib/ \
	  cython/package/example/__pycache__/ \
	  cython/use_cimport/build/ \
	  cython/venv/ \
	  f2py/__pycache__/ \
	  f2py/example$(EXT_SUFFIX).dSYM/ \
	  python/__pycache__/

.PHONY: all run-fortran run-c run-ctypes run-cffi run-f2py broken-f2py run-cython broken-cython inspect-cython-sdist inspect-cython-installed wrap-cython run-golang clean

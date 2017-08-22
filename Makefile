CC          = gcc
FC          = gfortran
MODULES_DIR = -J
FORTRAN_LIB = -lgfortran
PYTHON      = python
PIC         = -shared -fPIC
F2PY        = f2py
EXT_SUFFIX  = $(shell $(PYTHON) -c 'import distutils.sysconfig as DS; print(DS.get_config_var("EXT_SUFFIX"))')
ROOT_DIR   := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

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
	  $(FORTRAN_LIB)
	# OR: gfortran c/example.o fortran/example.o -o c_example

run-c: c_example
	@./c_example

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
	    skip: make_container

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

cython-install: cython/maybe_install.py cython/venv cython/package/setup.py cython/package/example/fast.c c/example.h fortran/example.f90
	@# Make sure our copied files are as expected. We use copies
	@# instead of symlinks because MANIFEST.in copies the **symlinks**.
	@diff --brief c/example.h cython/package/example/include/example.h
	@diff --brief fortran/example.f90 cython/package/example/example.f90
	@cython/venv/bin/python cython/maybe_install.py

run-cython: cython-install cython/check_cython.py
	@cython/venv/bin/python cython/check_cython.py

broken-cython: cython/package/setup.py cython/package/example/fast.c
	cd cython/package/ && \
	  IGNORE_LIBRARIES=true $(PYTHON) setup.py build_ext --inplace && \
	  $(PYTHON) -c 'import example'

run-golang: golang/main.go golang/src/example/example.go c/example.h fortran/example.f90
	@GOPATH=$(ROOT_DIR)/golang go run golang/main.go

clean:
	rm -f \
	  c/example.o \
	  c_example \
	  cython/example.mod \
	  cython/example/example.o \
	  cython/example/fast$(EXT_SUFFIX) \
	  f2py/example$(EXT_SUFFIX) \
	  fortran/example.mod \
	  fortran/example.o \
	  fortran_example \
	  golang/src/example/example.mod \
	  python/example.so
	rm -fr \
	  cython/__pycache__/ \
	  cython/build/ \
	  cython/example/__pycache__/ \
	  cython/venv \
	  f2py/__pycache__/ \
	  python/__pycache__/

.PHONY: all run-fortran run-c run-ctypes run-cffi run-f2py broken-f2py cython-install run-cython broken-cython run-golang clean

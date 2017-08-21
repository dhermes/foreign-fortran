CC          = gcc
FC          = gfortran
MODULES_DIR = -J
FORTRAN_LIB = -lgfortran
PYTHON      = python
PIC         = -shared -fPIC
F2PY        = f2py
EXT_SUFFIX  = $(shell $(PYTHON) -c 'import distutils.sysconfig as DS; print(DS.get_config_var("EXT_SUFFIX"))')

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

cython/example$(EXT_SUFFIX): cython/setup.py cython/example.pyx python/example.so
	$(FC) \
	  $(PIC) \
	  $(MODULES_DIR) fortran/ \
	  -c fortran/example.f90 \
	  -o cython/example.o
	cd cython/ && \
	  $(PYTHON) setup.py build_ext --inplace

run-cython: cython/check_cython.py cython/example$(EXT_SUFFIX)
	@$(PYTHON) cython/check_cython.py

clean:
	rm -f \
	  c/example.o \
	  c_example \
	  cython/example.c \
	  cython/example.o \
	  cython/example$(EXT_SUFFIX) \
	  f2py/example$(EXT_SUFFIX) \
	  fortran/example.mod \
	  fortran/example.o \
	  fortran_example \
	  python/example.so
	rm -fr \
	  cython/__pycache__/ \
	  cython/build/ \
	  f2py/__pycache__/ \
	  python/__pycache__/

.PHONY: all run-fortran run-c run-ctypes run-cffi run-f2py broken-f2py run-cython clean

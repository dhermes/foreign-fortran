FC          = gfortran
MODULES_DIR = -J
FORTRAN_LIB = -lgfortran
PYTHON      = python
PIC         = -shared -fPIC

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
	./fortran_example

c_example: c/example.c fortran/example.o
	gcc \
	  -c c/example.c \
	  -o c/example.o
	gcc \
	  c/example.o \
	  fortran/example.o \
	  -o c_example \
	  $(FORTRAN_LIB)
	# OR: gfortran c/example.o fortran/example.o -o c_example

run-c: c_example
	./c_example

python/example.so: fortran/example.f90
	$(FC) \
	  $(PIC) \
	  $(MODULES_DIR) fortran/ \
	  fortran/example.f90 \
	  -o python/example.so

run-ctypes: python/check_ctypes.py python/example.so
	$(PYTHON) python/check_ctypes.py

clean:
	rm -f \
	  c/example.o \
	  c_example \
	  fortran/example.mod \
	  fortran/example.o \
	  fortran_example \
	  python/example.so

.PHONY: all run-fortran run-c run-ctypes clean

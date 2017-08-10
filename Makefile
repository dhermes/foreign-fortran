all: main

main: example.mod example.o main.f90
	gfortran -o main main.f90 example.o

main_c: example.f90 main.c
	gcc -c main.c
	gfortran main.o example.f90 -o main_c
	rm main.o

cy_example.so: cy_example.pyx example.so
	gfortran -shared -fPIC -c example.f90
	python setup.py build_ext --inplace
	rm -fr build/ cy_example.c example.mod example.o example.so

example.so: example.f90
	gfortran -shared -fPIC example.f90 -o example.so

fortran_example.so: example.f90 .f2py_f2cmap
	f2py --verbose -c --opt='-O3' -m fortran_example example.f90 \
	skip: make_container

fortran_broken: example.f90 .f2py_f2cmap
	f2py --verbose -c --opt='-O3' -m fortran_example example.f90 \
	only: make_container

example.o example.mod: example.f90
	gfortran -c example.f90

clean:
	rm -f cy_example.so example.mod example.o example.so fortran_example.so main main_c

.PHONY: all fortran_broken clean

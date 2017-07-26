all: main

main: example.mod example.o main.f90 types.mod
	gfortran -o main main.f90 example.o

main_c: example.f90 main.c types.mod
	gcc -c main.c example.f90 types.f90
	gfortran main.o example.f90 types.f90 -o main_c
	rm main.o
	rm types.o

example.so: example.f90 types.mod
	gfortran -shared -fPIC example.f90 -o example.so

fortran_example.so: example.f90 .f2py_f2cmap types.mod
	f2py --verbose -c --opt='-O3' -m fortran_example example.f90 \
	skip: make_udf

example.o example.mod: example.f90 types.mod
	gfortran -c example.f90

types.mod: types.f90
	gfortran -c types.f90
	rm types.o

clean:
	rm -f example.mod example.o example.so fortran_example.so main main_c types.mod

.PHONY: all clean

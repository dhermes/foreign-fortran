all: main

main: example.mod types.mod main.f90 example.o
	gfortran -o main main.f90 example.o

fortran_example.so: example.f90 .f2py_f2cmap types.mod
	f2py --verbose -c --opt='-O3' -m fortran_example example.f90

example.o example.mod: example.f90 types.mod
	gfortran -c example.f90

types.mod: types.f90
	gfortran -c types.f90
	rm types.o

clean:
	rm -f example.mod example.o fortran_example.so main types.mod

.PHONY: all clean

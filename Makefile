all: main

main: example.mod types.mod main.f90 example.o
	gfortran -o main main.f90 example.o

example.o example.mod: example.f90 types.mod
	gfortran -c example.f90

types.mod: types.f90
	gfortran -c types.f90
	rm types.o

clean:
	rm -f example.mod example.o main types.mod

.PHONY: all clean

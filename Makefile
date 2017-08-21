FC = gfortran

all: fortran_example

fortran_example: fortran/example.mod fortran/example.o fortran/main.f90
	$(FC) -o fortran_example fortran/main.f90 fortran/example.o

run-fortran: fortran_example
	./fortran_example

fortran/example.o fortran/example.mod: fortran/example.f90
	$(FC) -J fortran/ -c fortran/example.f90 -o fortran/example.o

clean:
	rm -f \
	  fortran/example.mod \
	  fortran/example.o \
	  fortran_example

.PHONY: all clean

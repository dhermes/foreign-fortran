#include <stdint.h>

struct UserDefined {
  double buzz;
  double broken;
  int how_many;
};

struct DataContainer {
  double data[8];
};

void foo(double bar, double baz, double *quux);
void __example_MOD_foo_by_ref(double *bar, double *baz, double *quux);
void foo_array(int *size, double *val, double *two_val);
void make_udf(double *buzz, double *broken, int *how_many, struct UserDefined *quuz);
void udf_ptr(intptr_t *ptr_as_int);
void make_container(double *contained, struct DataContainer *container);
void just_print(void);

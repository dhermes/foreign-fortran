#if defined (__cplusplus)
#include <cstdint>
extern "C" {
#else
#include <stdint.h>
#endif

typedef struct {
  double buzz;
  double broken;
  int how_many;
} UserDefined;

typedef struct {
  double data[8];
} DataContainer;

void foo(double bar, double baz, double *quux);
void __example_MOD_foo_by_ref(double *bar, double *baz, double *quux);
void foo_array(int *size, double *val, double *two_val);
void make_udf(double *buzz, double *broken, int *how_many, UserDefined *quuz);
void udf_ptr(intptr_t *ptr_as_int);
void make_container(double *contained, DataContainer *container);
void just_print(void);

#if defined (__cplusplus)
}
#endif

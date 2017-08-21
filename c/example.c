#include <stdint.h>
#include <stdio.h>
#include <math.h>

#include "example.h"

void print_sep (void)
{
  printf("------------------------------------------------------------\n");
}

int main (void)
{
  print_sep();
  // foo()
  double bar = 1.0, baz = 16.0, quux;
  foo(bar, baz, &quux);
  printf("quux = foo(%f, %f) = %f\n", bar, baz, quux);

  print_sep();
  // make_udf()
  double buzz = 1.25, broken = 5.0;
  int how_many = 1337;
  struct UserDefined quuz;
  make_udf(&buzz, &broken, &how_many, &quuz);
  printf("quuz = make_udf(%f, %f, %d)\n     = UserDefined(%f, %f, %d)\n",
         buzz, broken, how_many,
         quuz.buzz, quuz.broken, quuz.how_many);

  print_sep();
  // foo_array()
  int size = 4;
  double val[8] = {3.0, 1.0, 9.0, -1.0, 4.5, 1.25, 0.0, 4.0};
  double two_val[8];
  foo_array(&size, val, two_val);
  printf("foo_array(\n");
  printf("    %d,\n", size);
  printf("    [[%f, %f],\n", val[0], val[4]);
  printf("     [%f, %f],\n", val[1], val[5]);
  printf("     [%f, %f],\n", val[2], val[6]);
  printf("     [%f, %f]],\n", val[3], val[7]);
  printf(") =\n");
  printf("    [[%f, %f],\n", two_val[0], two_val[4]);
  printf("     [%f, %f],\n", two_val[1], two_val[5]);
  printf("     [%f, %f],\n", two_val[2], two_val[6]);
  printf("     [%f, %f]]\n", two_val[3], two_val[7]);

  print_sep();
  // udf_ptr()
  struct UserDefined made_it;
  intptr_t ptr_as_int = (intptr_t) (&made_it);
  udf_ptr(&ptr_as_int);
  printf("ptr_as_int = &made_it  // intptr_t / ssize_t / long\n");
  printf("ptr_as_int = %ld  // %p\n", ptr_as_int, ptr_as_int);
  printf("udf_ptr(ptr_as_int)  // Set memory in ``made_it``\n");
  printf("made_it = UserDefined(%f, %f, %d)\n",
         made_it.buzz, made_it.broken, made_it.how_many);

  print_sep();
  // make_container()
  double contained[8] = {0.0, 1.0, 1.0, 3.0, 4.0, 9.0, 2.0, 1.0};
  struct DataContainer container;
  printf("contained =\n");
  printf("  [[%f, %f],\n", contained[0], contained[4]);
  printf("   [%f, %f],\n", contained[1], contained[5]);
  printf("   [%f, %f],\n", contained[2], contained[6]);
  printf("   [%f, %f]]\n", contained[3], contained[7]);
  make_container(contained, &container);
  printf("container = make_container(contained)\n");
  printf("container.data =\n");
  printf("  [[%f, %f],\n", container.data[0], container.data[4]);
  printf("   [%f, %f],\n", container.data[1], container.data[5]);
  printf("   [%f, %f],\n", container.data[2], container.data[6]);
  printf("   [%f, %f]]\n", container.data[3], container.data[7]);
  printf("&contained      = %ld  // %p\n", contained, contained);
  printf("&container      = %ld  // %p\n", &container, &container);
  printf("&container.data = %ld  // %p\n", container.data, container.data);

  print_sep();
  // just_print()
  printf("just_print()\n");
  just_print();

  return 0;
}

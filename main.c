#include <stdio.h>
#include <math.h>

int main (void)
{
  double bar = 1.0, baz = 16.0, quux;
  foo(bar, baz, &quux);
  printf("quux = foo(%f, %f) = %f\n", bar, baz, quux);
  return 0;
}

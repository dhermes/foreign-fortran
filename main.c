#include <stdio.h>
#include <math.h>

struct UserDefined {
  double buzz;
  double broken;
  int how_many;
};

int main (void)
{
  double bar = 1.0, baz = 16.0, quux;
  foo(bar, baz, &quux);
  printf("quux = foo(%f, %f) = %f\n", bar, baz, quux);

  double buzz = 1.25, broken = 5.0;
  int how_many = 1337;
  struct UserDefined quuz;
  make_udf(buzz, broken, how_many, &quuz);
  printf("quuz = make_udf(%f, %f, %d) = UserDefined(%f, %f, %d)\n",
         buzz, broken, how_many,
         quuz.buzz, quuz.broken, quuz.how_many);

  return 0;
}

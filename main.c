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

  int size = 4;
  double val[8] = {3.0, 1.0, 9.0, -1.0, 4.5, 1.25, 0.0, 4.0};
  double two_val[8];
  foo_array(size, &val, &two_val);
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

  struct UserDefined *made_it_ptr;
  udf_ptr(&made_it_ptr);
  struct UserDefined made_it = *made_it_ptr;
  printf("made_it_ptr = %p\n", made_it_ptr);
  printf("made_it_ptr = %ld\n", made_it_ptr);
  printf("made_it = UserDefined(%f, %f, %d)\n",
         made_it.buzz, made_it.broken, made_it.how_many);

  return 0;
}

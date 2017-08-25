#include <cstdint>
#include <iomanip>
#include <iostream>
#include <string>

#include "example.h"

void print_sep (void)
{
  std::cout << std::string(60, '-') << std::endl;
}

int main ()
{
  // Applies throughout.
  std::cout << std::fixed << std::setprecision(6);

  print_sep();
  // foo()
  double bar = 1.0, baz = 16.0, quux;
  foo(bar, baz, &quux);
  std::cout <<
    "quux = foo(" << bar << ", " << baz << ") = " <<
    quux << std::endl;

  print_sep();
  // make_udf()
  double buzz = 1.25, broken = 5.0;
  int how_many = 1337;
  UserDefined quuz;
  make_udf(&buzz, &broken, &how_many, &quuz);
  std::cout <<
    "quuz = make_udf(" << buzz << ", " << broken << ", " <<
    how_many << ")" << std::endl;
  std::cout <<
    "     = UserDefined(" <<
    quuz.buzz << ", " <<
    quuz.broken << ", " <<
    quuz.how_many << ")" <<
    std::endl;

  print_sep();
  // just_print()
  std::cout << "just_print()" << std::endl;
  just_print();

  return 0;
}

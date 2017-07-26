program main

  use types, only: dp
  use example, only: foo, make_udf, UserDefined
  implicit none

  real(dp) :: bar, baz, quux
  real(dp) :: buzz, broken
  integer :: how_many
  type(UserDefined) :: quuz

  bar = 1.0_dp
  baz = 16.0_dp
  call foo(bar, baz, quux)

  buzz = 1.25_dp
  broken = 5.0_dp
  how_many = 1337
  call make_udf(buzz, broken, how_many, quuz)

  print *, "foo(", bar, baz, ") = ", quux
  print *, "make_udf(", buzz, broken, how_many, ")"
  print *, "       = ", quuz

end

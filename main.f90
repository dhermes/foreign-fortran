program main

  use types, only: dp
  use example, only: foo, make_udf, UserDefined
  implicit none

  real(dp) :: bar, baz, quux
  type(UserDefined) :: quuz

  bar = 1.0_dp
  baz = 16.0_dp
  call foo(bar, baz, quux)

  call make_udf(1.25_dp, 5.0_dp, 1337, quuz)

  print *, "bar =", bar
  print *, "baz =", baz
  print *, "quux =", quux
  print *, quuz

end

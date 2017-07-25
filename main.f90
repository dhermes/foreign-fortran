program main

  use types, only: dp
  use example, only: foo, UserDefined
  implicit none

  real(dp) :: bar, baz, quux
  type(UserDefined) :: quuz

  bar = 1.0_dp
  baz = 16.0_dp
  call foo(bar, baz, quux)

  quuz%buzz = 1.25_dp
  quuz%broken = 5.0_dp
  quuz%how_many = 1337

  print *, "LIFE"
  print *, quux
  print *, quuz

end

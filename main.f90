program main

  use types, only: dp
  use example, only: foo
  implicit none

  real(dp) :: bar, baz, quux

  bar = 1.0_dp
  baz = 16.0_dp
  call foo(bar, baz, quux)

  print *, "LIFE"
  print *, quux

end

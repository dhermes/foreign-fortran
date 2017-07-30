program main

  use example, only: dp, foo, foo_array, make_udf, UserDefined
  implicit none

  real(dp) :: bar, baz, quux
  real(dp) :: buzz, broken
  integer :: how_many
  type(UserDefined) :: quuz
  integer :: size_
  real(dp) :: val(4, 2), two_val(4, 2)

  call print_sep()
  ! foo()
  bar = 1.0_dp
  baz = 16.0_dp
  call foo(bar, baz, quux)
  print *, "foo(", bar, baz, ") = ", quux

  call print_sep()
  ! make_udf()
  buzz = 1.25_dp
  broken = 5.0_dp
  how_many = 1337
  call make_udf(buzz, broken, how_many, quuz)
  print *, "make_udf(", buzz, broken, how_many, ")"
  print *, "       = ", quuz

  call print_sep()
  ! foo_array()
  val = reshape((/ &
       3.0_dp, 1.0_dp, 9.0_dp, -1.0_dp, &
       4.5_dp, 1.25_dp, 0.0_dp, 4.0_dp/), &
       (/4, 2/))
  size_ = size(val, 1)
  call foo_array(size_, val, two_val)
  print *, "foo_array("
  print *, "    ", size_, ","
  print *, "    [[", val(1, 1), val(1, 2), "],"
  print *, "     [", val(2, 1), val(2, 2), "],"
  print *, "     [", val(3, 1), val(3, 2), "],"
  print *, "     [", val(4, 1), val(4, 2), "]],"
  print *, ") = "
  print *, "    [[", two_val(1, 1), two_val(1, 2), "],"
  print *, "     [", two_val(2, 1), two_val(2, 2), "],"
  print *, "     [", two_val(3, 1), two_val(3, 2), "],"
  print *, "     [", two_val(4, 1), two_val(4, 2), "]]"

end program

subroutine print_sep()

  print *, "------------------------------------------------------------"

end subroutine print_sep

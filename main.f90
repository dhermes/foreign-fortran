program main

  use iso_c_binding, only: c_ptr, c_intptr_t, c_loc
  use example, only: dp, foo, foo_array, make_udf, udf_ptr, &
                     just_print, UserDefined
  implicit none

  ! For foo()
  real(dp) :: bar, baz, quux
  ! For make_udf()
  real(dp) :: buzz, broken
  integer :: how_many
  type(UserDefined) :: quuz
  ! For foo_array()
  integer :: size_
  real(dp) :: val(4, 2), two_val(4, 2)
  ! For udf_ptr()
  integer(c_intptr_t) :: ptr_as_int
  type(c_ptr) :: made_it_ptr
  type(UserDefined), target :: made_it

  call print_sep()
  ! foo()
  bar = 1.0_dp
  baz = 16.0_dp
  call foo(bar, baz, quux)
  write (*, "(A, F8.6, A, F9.6, A, F9.6)") &
       "quux = foo(", bar, ", ", baz, ") = ", quux

  call print_sep()
  ! make_udf()
  buzz = 1.25_dp
  broken = 5.0_dp
  how_many = 1337
  call make_udf(buzz, broken, how_many, quuz)
  write (*, "(A, F8.6, A, F8.6, A, I4, A)") &
       "quuz = make_udf(", buzz, ", ", broken, ", ", how_many, ")"
  write (*, "(A, F8.6, A, F8.6, A, I4, A)") &
       "     = UserDefined(", quuz%buzz, ", ", quuz%broken, &
       ", ", quuz%how_many, ")"

  call print_sep()
  ! foo_array()
  val = reshape((/ &
       3.0_dp, 1.0_dp, 9.0_dp, -1.0_dp, &
       4.5_dp, 1.25_dp, 0.0_dp, 4.0_dp/), &
       (/4, 2/))
  size_ = size(val, 1)
  call foo_array(size_, val, two_val)
  write (*, "(A)"), "foo_array("
  write (*, "(A, I1, A)"), "    ", size_, ","
  write (*, "(A, F8.6, A, F8.6, A)"), "    [[", val(1, 1), ", ", val(1, 2), "],"
  write (*, "(A, F8.6, A, F8.6, A)"), "     [", val(2, 1), ", ", val(2, 2), "],"
  write (*, "(A, F8.6, A, F8.6, A)"), "     [", val(3, 1), ", ", val(3, 2), "],"
  write (*, "(A, F9.6, A, F8.6, A)"), &
       "     [", val(4, 1), ", ", val(4, 2), "]],"
  write (*, "(A)"), ") ="
  write (*, "(A, F8.6, A, F8.6, A)"), &
       "    [[", two_val(1, 1), ", ", two_val(1, 2), "],"
  write (*, "(A, F8.6, A, F8.6, A)"), &
       "     [", two_val(2, 1), ", ", two_val(2, 2), "],"
  write (*, "(A, F9.6, A, F8.6, A)"), &
       "     [", two_val(3, 1), ", ", two_val(3, 2), "],"
  write (*, "(A, F9.6, A, F8.6, A)"), &
       "     [", two_val(4, 1), ", ", two_val(4, 2), "]]"

  call print_sep()
  ! udf_ptr()
  made_it_ptr = c_loc(made_it)
  ptr_as_int = transfer(made_it_ptr, ptr_as_int)
  call udf_ptr(ptr_as_int)
  write (*, "(A, I15, A, Z12, A)"), &
       "ptr_as_int = ", ptr_as_int, " (0x", ptr_as_int, ")"
  write (*, "(A, F8.6, A, F10.6, A, I3, A)") &
       "made_it = UserDefined(", made_it%buzz, ", ", made_it%broken, &
       ", ", made_it%how_many, ")"

  call print_sep()
  ! just_print()
  write (*, "(A)"), "just_print()"
  call just_print()

end program

subroutine print_sep()

  write (*, "(A)") "------------------------------------------------------------"

end subroutine print_sep

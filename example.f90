module example

  use iso_c_binding, only: c_double, c_int, c_ptr, c_loc
  implicit none
  private
  public dp, foo, foo_array, foo_not_c, make_udf, udf_ptr, UserDefined

  integer, parameter :: dp=kind(0.d0)

  type, bind(c) :: UserDefined
     real(c_double) :: buzz
     real(c_double) :: broken
     integer(c_int) :: how_many
  end type UserDefined

contains

  subroutine foo(bar, baz, quux) bind(c, name='foo')
    real(c_double), intent(in), value :: bar, baz
    real(c_double), intent(out) :: quux

    quux = bar + 3.75_dp * baz

  end subroutine foo

  subroutine foo_array(size_, val, two_val) bind(c, name='foo_array')
    integer(c_int), intent(in) :: size_
    real(c_double), intent(in) :: val(size_, 2)
    real(c_double), intent(out) :: two_val(size_, 2)

    two_val = 2.0_dp * val

  end subroutine foo_array

  subroutine foo_not_c(bar, baz, quux)
    real(dp), intent(in) :: bar, baz
    real(dp), intent(out) :: quux

    quux = bar + 3.75_dp * baz

  end subroutine foo_not_c

  subroutine make_udf(buzz, broken, how_many, made_it) bind(c, name='make_udf')
    real(c_double), intent(in), value :: buzz, broken
    integer(c_int), intent(in), value :: how_many
    type(UserDefined), intent(out) :: made_it

    made_it%buzz = buzz
    made_it%broken = broken
    made_it%how_many = how_many

  end subroutine make_udf

  subroutine udf_ptr(made_it_ptr) bind(c, name='udf_ptr')
    type(c_ptr), intent(out) :: made_it_ptr
    ! Outside of signature
    type(UserDefined), target :: made_it

    made_it%buzz = 3.125_dp
    made_it%broken = -10.5_dp
    made_it%how_many = 101

    made_it_ptr = c_loc(made_it)

  end subroutine udf_ptr

end module example

module example

  use iso_c_binding, only: c_double, c_int
  use types, only: dp
  implicit none
  private
  public foo, make_udf, UserDefined

  type, bind(c) :: UserDefined
     real(c_double) :: buzz
     real(c_double) :: broken
     integer(c_int) :: how_many
  end type UserDefined

contains

  subroutine foo(bar, baz, quux) bind(c)
    real(c_double), intent(in), value :: bar, baz
    real(c_double), intent(out) :: quux

    quux = bar + 3.75_dp * baz

  end subroutine foo

  subroutine make_udf(buzz, broken, how_many, made_it)
    real(c_double), intent(in) :: buzz, broken
    integer(c_int), intent(in) :: how_many
    type(UserDefined), intent(out) :: made_it

    made_it%buzz = buzz
    made_it%broken = broken
    made_it%how_many = how_many

  end subroutine make_udf

end module example

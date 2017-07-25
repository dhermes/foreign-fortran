module example

  use types, only: dp
  implicit none
  private
  public foo, make_udf, UserDefined

  type UserDefined
     real(dp) :: buzz
     real(dp) :: broken
     integer :: how_many
  end type UserDefined

contains

  subroutine foo(bar, baz, quux)
    real(dp), intent(in) :: bar, baz
    real(dp), intent(out) :: quux

    quux = bar + 3.75_dp * baz

  end subroutine foo

  subroutine make_udf(buzz, broken, how_many, made_it)
    real(dp), intent(in) :: buzz, broken
    integer, intent(in) :: how_many
    type(UserDefined), intent(out) :: made_it

    made_it%buzz = buzz
    made_it%broken = broken
    made_it%how_many = how_many

  end subroutine make_udf

end module example

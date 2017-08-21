module example

  use iso_c_binding, only: c_double, c_int, c_ptr, c_intptr_t, &
                           c_char, c_f_pointer
  implicit none
  private
  public dp, foo, foo_array, foo_by_ref, make_udf, udf_ptr, &
         just_print, UserDefined

  integer, parameter :: dp=kind(0.d0)

  type, bind(c) :: UserDefined
     ! sequence NOT NEEDED since bind(c) is used.
     real(c_double) :: buzz
     real(c_double) :: broken
     integer(c_int) :: how_many
  end type UserDefined

  type, bind(c) :: DataContainer
     real(c_double) :: data(4, 2)
  end type DataContainer

contains

  subroutine foo(bar, baz, quux) bind(c, name='foo')
    real(c_double), intent(in), value :: bar, baz
    real(c_double), intent(out) :: quux

    quux = bar + 3.75_dp * baz

  end subroutine foo

  subroutine foo_by_ref(bar, baz, quux)
    real(dp), intent(in) :: bar, baz
    real(dp), intent(out) :: quux

    call foo(bar, baz, quux)

  end subroutine foo_by_ref

  subroutine foo_array(size_, val, two_val) bind(c, name='foo_array')
    integer(c_int), intent(in) :: size_
    real(c_double), intent(in) :: val(size_, 2)
    real(c_double), intent(out) :: two_val(size_, 2)

    two_val = 2.0_dp * val

  end subroutine foo_array

  subroutine make_udf(buzz, broken, how_many, as_bytes) bind(c, name='make_udf')
    real(c_double), intent(in) :: buzz, broken
    integer(c_int), intent(in) :: how_many
    character(c_char), intent(out) :: as_bytes(24)
    ! Outside of signature
    type(UserDefined), target :: made_it

    made_it%buzz = buzz
    made_it%broken = broken
    made_it%how_many = how_many

    ! NOTE: We need ``sizeof(as_bytes) == sizeof(made_it)``
    as_bytes = transfer(made_it, as_bytes)

  end subroutine make_udf

  subroutine udf_ptr(ptr_as_int) bind(c, name='udf_ptr')
    integer(c_intptr_t), intent(in) :: ptr_as_int
    ! Outside of signature
    type(c_ptr) :: made_it_ptr
    type(UserDefined), pointer :: made_it

    made_it_ptr = transfer(ptr_as_int, made_it_ptr)
    call c_f_pointer(made_it_ptr, made_it)

    made_it%buzz = 3.125_dp
    made_it%broken = -10.5_dp
    made_it%how_many = 101

  end subroutine udf_ptr

  subroutine make_container(contained, container) &
       bind(c, name='make_container')
    real(c_double), intent(in) :: contained(4, 2)
    type(DataContainer), intent(out) :: container

    container%data = contained

  end subroutine make_container

  subroutine just_print() bind(c, name='just_print')

    print *, "======== BEGIN FORTRAN ========"
    print *, "just_print() was called"
    print *, "========  END  FORTRAN ========"

  end subroutine just_print

end module example

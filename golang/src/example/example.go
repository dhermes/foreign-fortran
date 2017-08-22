package example

// #include "example.h"
import "C"

type UserDefined struct {
	Buzz    float64
	Broken  float64
	HowMany int32
}

func JustPrint() {
	C.just_print()
}

func Foo(bar, baz float64) float64 {
	var quux float64
	C.foo(
		C.double(bar),
		C.double(baz),
		(*C.double)(&quux),
	)
	return quux
}

func MakeUDF(buzz, broken float64, howMany int32) UserDefined {
	var quuz C.struct_UserDefined
	C.make_udf(
		(*C.double)(&buzz),
		(*C.double)(&broken),
		(*C.int)(&howMany),
		&quuz,
	)
	return UserDefined{
		*(*float64)(&quuz.buzz),
		*(*float64)(&quuz.broken),
		*(*int32)(&quuz.how_many),
	}
}

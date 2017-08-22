package example

import "fmt"

// #include "example.h"
import "C"

type UserDefined struct {
	Buzz    float64
	Broken  float64
	HowMany int32
}

func (udf *UserDefined) String() string {
	return fmt.Sprintf(
		"%T(%f, %f, %d)",
		udf, udf.Buzz, udf.Broken, udf.HowMany,
	)
}

func JustPrint() {
	C.just_print()
}

func Foo(bar, baz *float64) float64 {
	var quux float64
	// NOTE: Could've just passed ``bar`` and ``baz`` by value and
	//       done ``C.double(bar)``, but that would involve an
	//       unnecessary copy. (It is a moot, since that is somewhat
	//       the point of pass by value.)
	C.foo(
		*(*C.double)(bar),
		*(*C.double)(baz),
		(*C.double)(&quux),
	)
	return quux
}

func MakeUDF(buzz, broken *float64, howMany *int32) *UserDefined {
	var quuz C.struct_UserDefined
	C.make_udf(
		(*C.double)(buzz),
		(*C.double)(broken),
		(*C.int)(howMany),
		&quuz,
	)
	return &UserDefined{
		*(*float64)(&quuz.buzz),
		*(*float64)(&quuz.broken),
		*(*int32)(&quuz.how_many),
	}
}

func FooArray(size *int32, val []float64) []float64 {
	twoVal := make([]float64, len(val), cap(val))
	C.foo_array(
		(*C.int)(size),
		(*C.double)(&val[0]),
		(*C.double)(&twoVal[0]),
	)
	return twoVal
}

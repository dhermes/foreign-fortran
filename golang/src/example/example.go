package example

// #include "example.h"
import "C"

func JustPrint() {
	C.just_print()
}

func Foo(bar, baz float64) float64 {
	var quux C.double
	C.foo(
		C.double(bar),
		C.double(baz),
		&quux,
	)
	return float64(quux)
}

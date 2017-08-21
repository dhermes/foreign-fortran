package example

// #include "example.h"
import "C"

func JustPrint() {
	C.just_print()
}

package main

import (
	"example"
	"fmt"
	"strings"
)

var separator = strings.Repeat("-", 60)

func main() {
	fmt.Println(separator)
	// foo()
	bar := 1.0
	baz := 16.0
	quux := example.Foo(bar, baz)
	fmt.Printf("quux = foo(%f, %f) = %f\n", bar, baz, quux)

	fmt.Println(separator)
	// make_udf()
	buzz := 1.25
	broken := 5.0
	howMany := int32(1337)
	quuz := example.MakeUDF(buzz, broken, howMany)
	fmt.Printf(
		"quuz = make_udf(%f, %f, %d)\n",
		buzz, broken, howMany,
	)
	fmt.Printf("     = %T(%v)\n", quuz, quuz)

	fmt.Println(separator)
	// just_print()
	fmt.Println("just_print()")
	example.JustPrint()
}

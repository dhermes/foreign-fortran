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
	// just_print()
	fmt.Println("just_print()")
	example.JustPrint()
}

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
	quux := example.Foo(&bar, &baz)
	fmt.Printf("quux = foo(%f, %f) = %f\n", bar, baz, quux)

	fmt.Println(separator)
	// make_udf()
	buzz := 1.25
	broken := 5.0
	howMany := int32(1337)
	quuz := example.MakeUDF(&buzz, &broken, &howMany)
	fmt.Printf(
		"quuz = make_udf(%f, %f, %d)\n     = %v\n",
		buzz, broken, howMany, quuz,
	)

	fmt.Println(separator)
	// foo_array()
	size := int32(4)
	val := []float64{3.0, 1.0, 9.0, -1.0, 4.5, 1.25, 0.0, 4.0}
	twoVal := example.FooArray(&size, val)
	fmt.Println("foo_array(")
	fmt.Printf("    %d,\n", size)
	fmt.Printf("    [[%f, %f],\n", val[0], val[4])
	fmt.Printf("     [%f, %f],\n", val[1], val[5])
	fmt.Printf("     [%f, %f],\n", val[2], val[6])
	fmt.Printf("     [%f, %f]],\n", val[3], val[7])
	fmt.Printf(") =\n")
	fmt.Printf("    [[%f, %f],\n", twoVal[0], twoVal[4])
	fmt.Printf("     [%f, %f],\n", twoVal[1], twoVal[5])
	fmt.Printf("     [%f, %f],\n", twoVal[2], twoVal[6])
	fmt.Printf("     [%f, %f]]\n", twoVal[3], twoVal[7])

	fmt.Println(separator)
	// just_print()
	fmt.Println("just_print()")
	example.JustPrint()
}

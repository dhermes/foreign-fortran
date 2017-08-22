package main

import (
	"example"
	"fmt"
	"strings"
	"unsafe"
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
	// udf_ptr()
	madeIt := example.UserDefined{}
	ptrAsInt := uintptr(unsafe.Pointer(&madeIt))
	example.UDFPtr(&ptrAsInt)
	fmt.Println("ptrAsInt = &madeIt")
	fmt.Printf("ptrAsInt = %d  // 0x%x\n", ptrAsInt, ptrAsInt)
	fmt.Println("udf_ptr(&ptrAsInt)  // Set memory in ``madeIt``")
	fmt.Printf("&madeIt = %v\n", &madeIt)

	fmt.Println(separator)
	// make_container()
	contained := [8]float64{0.0, 1.0, 1.0, 3.0, 4.0, 9.0, 2.0, 1.0}
	fmt.Println("contained =")
	fmt.Printf("  [[%f, %f],\n", contained[0], contained[4])
	fmt.Printf("   [%f, %f],\n", contained[1], contained[5])
	fmt.Printf("   [%f, %f],\n", contained[2], contained[6])
	fmt.Printf("   [%f, %f]]\n", contained[3], contained[7])
	container := example.MakeContainer(contained[:])
	fmt.Println("container = make_container(contained)")
	fmt.Println("container.Data =")
	fmt.Printf("  [[%f, %f],\n", container.Data[0], container.Data[4])
	fmt.Printf("   [%f, %f],\n", container.Data[1], container.Data[5])
	fmt.Printf("   [%f, %f],\n", container.Data[2], container.Data[6])
	fmt.Printf("   [%f, %f]]\n", container.Data[3], container.Data[7])
	ptrAsInt = uintptr(unsafe.Pointer(&contained[0]))
	fmt.Printf("&contained      = %d  // 0x%x\n", ptrAsInt, ptrAsInt)
	ptrAsInt = uintptr(unsafe.Pointer(&container))
	fmt.Printf("&container      = %d  // 0x%x\n", ptrAsInt, ptrAsInt)
	ptrAsInt = uintptr(unsafe.Pointer(&container.Data[0]))
	fmt.Printf("&container.Data = %d  // 0x%x\n", ptrAsInt, ptrAsInt)

	fmt.Println(separator)
	// just_print()
	fmt.Println("just_print()")
	example.JustPrint()
}

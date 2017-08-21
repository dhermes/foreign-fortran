package main

import (
	"example"
	"fmt"
	"strings"
)

var separator = strings.Repeat("-", 60)

func main() {
	fmt.Println(separator)
	fmt.Println("just_print()")
	example.JustPrint()
}

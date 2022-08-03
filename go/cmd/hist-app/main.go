package main

import (
	"log"

	"org.hbb/algo-trading/go/internal/historical"
)

// This is used to create the CSV files that are used by the python modules for back testing strategies.
func main() {
	log.Println("Starting historical app..")
	historical.Start()
}

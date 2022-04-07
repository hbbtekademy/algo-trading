package main

import (
	"log"

	"org.hbb/algo-trading/go/internal/historical"
)

func main() {
	log.Println("Starting historical app..")
	historical.Start()
}

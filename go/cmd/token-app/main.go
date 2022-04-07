package main

import (
	"log"

	tokenservice "org.hbb/algo-trading/go/internal/token"
)

func main() {
	log.Println("Starting Access Token Service")
	tokenservice.Start()
}

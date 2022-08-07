package main

import (
	"log"

	tokenService "org.hbb/algo-trading/go/internal/token"
)

func main() {
	log.Println("Starting Access Token Service")
	tokenService.Start()
}

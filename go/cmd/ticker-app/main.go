package main

import (
	"log"

	ticker "org.hbb/algo-trading/go/internal/ticker"
)

// This is the main entry point. The program starts from here.
func main() {
	log.Println("Starting ticker app...")
	ticker.Start()
}

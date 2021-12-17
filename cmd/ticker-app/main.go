package main

import (
	"log"

	ticker "org.hbb/algo-trading/internal/ticker"
)

func main() {
	log.Println("Starting ticker app...")
	ticker.Start()
}

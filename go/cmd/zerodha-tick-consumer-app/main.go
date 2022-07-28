package main

import (
	"log"
	ticker "org.hbb/algo-trading/go/internal/ticker"
)

// This is the entry point. Consumption of tick data kicked off from this "main"
func main() {
	log.Println("Starting Zerodha Tick Consumer app...")
	ticker.Start()
}

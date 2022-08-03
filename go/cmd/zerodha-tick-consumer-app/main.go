package main

import (
	"log"
	zerodhaDataConsumer "org.hbb/algo-trading/go/internal/zerodha"
)

// This is the entry point. Consumption of tick data kicked off from this "main"
func main() {
	log.Println("Starting Zerodha Tick Consumer app...")
	zerodhaDataConsumer.Start()
}

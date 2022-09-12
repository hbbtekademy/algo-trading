package main

import (
	"log"

	angelOneHistoricalDataConsumer "org.hbb/algo-trading/go/internal/data-consumer-services/historical/angel_one"
)

// This is the entry point. Consumption of tick data kicked off from this "main"
func main() {
	log.Println("Starting Angel One Tick Consumer app...")
	angelOneHistoricalDataConsumer.Start()
}

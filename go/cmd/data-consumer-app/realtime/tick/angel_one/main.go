package main

import (
	"log"

	angelOneDataConsumer "org.hbb/algo-trading/go/internal/data-consumer-services/realtime/angel_one"
)

// This is the entry point. Consumption of tick data kicked off from this "main"
func main() {
	log.Println("Starting Angel One Tick Consumer app...")
	angelOneDataConsumer.Start()
}

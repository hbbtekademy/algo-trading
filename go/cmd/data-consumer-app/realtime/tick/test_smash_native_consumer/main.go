package main

import (
	"log"

	smashNativeDataConsumer "org.hbb/algo-trading/go/internal/smash"
)

// This is the entry point. Consumption of tick data kicked off from this "main"
func main() {
	log.Println("Starting Smash Native Tick Consumer app...")
	smashNativeDataConsumer.Start()
}

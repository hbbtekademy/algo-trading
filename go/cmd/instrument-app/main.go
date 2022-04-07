package main

import (
	"log"
	"os"

	"github.com/gocarina/gocsv"
	"org.hbb/algo-trading/internal/instrument"
)

func main() {
	log.Println("Starting Instruments app...")
	instruments := instrument.GetKiteInstruments()

	instFile, err := os.OpenFile("../TickData/KiteInstruments.csv", os.O_RDWR|os.O_CREATE, os.ModePerm)
	if err != nil {
		log.Fatalln("Failed opening instrument file:", err)
	}

	err = gocsv.MarshalFile(instruments, instFile)
	if err != nil {
		log.Fatalln("Failed writing to csv file:", err)
	}
}

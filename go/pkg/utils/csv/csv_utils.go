package csv

import (
	"encoding/csv"
	"fmt"
	"log"
	"org.hbb/algo-trading/go/models"
	"os"
	"time"
)

func StreamTicksToFile(fileTickChannel chan *models.Tick, tickDataFile *os.File, instruments models.Instruments) {
	f, err := createTickFile()
	if err != nil {
		log.Fatalln("Error creating zerodha file: ", err)
	}
	defer func(f *os.File) {
		err := f.Close()
		if err != nil {
			log.Fatalln("Error closing zerodha file: ", err)
		}
	}(f)

	for {
		tick, ok := <-fileTickChannel
		if !ok {
			log.Printf("File Tick Channel closed. Exiting streamTicksToFile goroutine...")
			return
		}
		writeTickToCsvFile(tickDataFile, tick, instruments)
	}
}

func createTickFile() (*os.File, error) {
	var err error
	y, m, d := time.Now().Date()
	fn := fmt.Sprintf("Ticker-%d%d%d.csv", y, int(m), d)

	tickDataFile, err := os.OpenFile(fn, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Println("Error opening zerodha file:", err)
	}

	log.Printf("Tick file %s created...", fn)

	return tickDataFile, err
}

func writeTickToCsvFile(f *os.File, tick *models.Tick, instruments models.Instruments) {
	w := csv.NewWriter(f)
	defer w.Flush()

	err := w.Write(getTickData(tick, instruments))
	if err != nil {
		log.Fatalln("Error writing to zerodha file:", err)
	}
}

func getTickData(tick *models.Tick, instruments models.Instruments) []string {
	return []string{
		instruments[tick.InstrumentToken].Sym,
		tick.ExchangeTS.Format(time.RFC3339),
		tick.LastTradeTS.Format(time.RFC3339),
		fmt.Sprintf("%f", tick.LTP),
		fmt.Sprintf("%d", tick.LastTradedQuantity),
		fmt.Sprintf("%d", tick.VolumeTraded),
	}
}

package zerodha

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"time"

	"org.hbb/algo-trading/go/models"
)

func createTickFile() (*os.File, error) {
	var err error
	y, m, d := time.Now().Date()
	fn := fmt.Sprintf("Ticker-%d%d%d.csv", y, int(m), d)

	tickDataFile, err = os.OpenFile(fn, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Println("Error opening zerodha file:", err)
	}

	log.Printf("Tick file %s created...", fn)

	return tickDataFile, err
}

func writeTickToCsvFile(f *os.File, tick *models.Tick) {
	w := csv.NewWriter(f)
	defer w.Flush()

	err := w.Write(getTickData(tick))
	if err != nil {
		log.Fatalln("Error writing to zerodha file:", err)
	}
}

func getTickData(tick *models.Tick) []string {
	return []string{
		instruments[tick.InstrumentToken].Sym,
		tick.ExchangeTS.Format(time.RFC3339),
		tick.LastTradeTS.Format(time.RFC3339),
		fmt.Sprintf("%f", tick.LTP),
		fmt.Sprintf("%d", tick.LastTradedQuantity),
		fmt.Sprintf("%d", tick.VolumeTraded),
	}
}

func getInstrumentTokens() []uint32 {
	tokens := make([]uint32, 0, len(instruments))
	for k := range instruments {
		tokens = append(tokens, k)
	}
	return tokens
}

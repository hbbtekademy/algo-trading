package ticker

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"time"

	kitemodels "github.com/zerodha/gokiteconnect/v4/models"
)

func createTickFile() {
	var err error
	y, m, d := time.Now().Date()
	fn := fmt.Sprintf("Ticker-%d%d%d.csv", y, int(m), d)

	tickFile, err = os.OpenFile(fn, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalln("Error opening ticker file:", err)
	}

	log.Printf("Tick file %s created...", fn)
}

func writeToCsv(tick kitemodels.Tick) {
	w := csv.NewWriter(tickFile)
	defer w.Flush()

	err := w.Write(getTickData(tick))
	if err != nil {
		log.Fatalln("Error writing to ticker file:", err)
	}
}

func getTickData(tick kitemodels.Tick) []string {
	return []string{
		instruments[tick.InstrumentToken],
		tick.Timestamp.Format(time.RFC3339),
		tick.LastTradeTime.Format(time.RFC3339),
		fmt.Sprintf("%f", tick.LastPrice),
		fmt.Sprintf("%d", tick.LastTradedQuantity),
		fmt.Sprintf("%d", tick.VolumeTraded),
	}
}

func getInstTokens() []uint32 {
	tokens := make([]uint32, 0, len(instruments))
	for k := range instruments {
		tokens = append(tokens, k)
	}
	return tokens
}

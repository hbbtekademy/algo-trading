package ticker

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"time"

	kitemodels "github.com/zerodha/gokiteconnect/v4/models"
)

func createTickFile() (*os.File, error) {
	var err error
	y, m, d := time.Now().Date()
	fn := fmt.Sprintf("Ticker-%d%d%d.csv", y, int(m), d)

	tickFile, err = os.OpenFile(fn, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Println("Error opening ticker file:", err)
	}

	log.Printf("Tick file %s created...", fn)

	return tickFile, err
}

func writeTickToCsv(tick *kitemodels.Tick) {
	w := csv.NewWriter(tickFile)
	defer w.Flush()

	err := w.Write(getTickData(tick))
	if err != nil {
		log.Fatalln("Error writing to ticker file:", err)
	}
}

func writeTickToRedis(tick *kitemodels.Tick) {
	keyTS := tick.Timestamp.Time.Format("200601021504")
	keySym := tick.InstrumentToken

	ltpKey := fmt.Sprintf("LTP:ts:sym:%s:%d", keyTS, keySym)
	ltpValue := fmt.Sprintf("%f", tick.LastPrice)

	_, err := rdb.RPush(ctx, ltpKey, ltpValue).Result()
	if err != nil {
		log.Println("Failed pushing tick LTP to redis: ", err)
	}

	volKey := fmt.Sprintf("VOL:ts:sym:%s:%d", keyTS, keySym)
	volValue := fmt.Sprintf("%d", tick.VolumeTraded)

	_, err = rdb.Set(ctx, volKey, volValue, 0).Result()
	if err != nil {
		log.Println("Failed setting tick VOL to redis: ", err)
	}
}

func getTickData(tick *kitemodels.Tick) []string {
	return []string{
		instruments[tick.InstrumentToken].Sym,
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

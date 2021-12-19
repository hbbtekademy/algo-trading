package ticker

import (
	"log"
	"time"

	kitemodels "github.com/zerodha/gokiteconnect/v4/models"
	kiteticker "github.com/zerodha/gokiteconnect/v4/ticker"
)

func onTick(tick kitemodels.Tick) {
	//log.Println(getTickData(tick))
	if !(tick.Timestamp.After(mst) && tick.Timestamp.Before(met)) {
		log.Printf("ExchTS: %s outside market hours. Skipping tick", tick.Timestamp.Format(time.RFC3339))
		return
	}
	writeToCsv(tick)
}

func onConnect() {
	log.Println("Connected")

	err := ticker.Subscribe(getInstTokens())
	if err != nil {
		log.Fatalln(err)
	}

	err = ticker.SetMode(kiteticker.ModeFull, getInstTokens())
	if err != nil {
		log.Fatalln("Error setting Ticker Mode:", err)
	}
	log.Println("Tokens subscribed..")

	createTickFile()
}

func onReconnect(attempt int, delay time.Duration) {
	log.Println("Reconnecting...")
}

func onError(err error) {
	log.Println("Error streaming ticks:", err)
}

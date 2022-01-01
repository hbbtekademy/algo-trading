package ticker

import (
	"log"
	"time"

	kitemodels "github.com/zerodha/gokiteconnect/v4/models"
	kiteticker "github.com/zerodha/gokiteconnect/v4/ticker"
	"org.hbb/algo-trading/models"
	utils "org.hbb/algo-trading/pkg/utils"
)

var (
	fileTickCh  chan *models.Tick
	redisTickCh chan *models.Tick
	chClosed    bool
)

func onTick(kiteTick kitemodels.Tick) {
	//log.Println(getTickData(tick))
	// Close the channels 5 mins after market close
	tick := &models.Tick{
		InstrumentToken:    kiteTick.InstrumentToken,
		Sym:                instruments[kiteTick.InstrumentToken].Sym,
		ExchTS:             kiteTick.Timestamp.Time,
		LastTradeTS:        kiteTick.LastTradeTime.Time,
		LTP:                float32(kiteTick.LastPrice),
		LastTradedQuantity: kiteTick.LastTradedQuantity,
		VolumeTraded:       kiteTick.VolumeTraded,
	}

	if mktutil.IsAfterMarketHrs(time.Now().Add(-5*time.Minute)) && !chClosed {
		log.Printf("Current Time: %s after mkt hrs. Closing File and Redis channels...",
			time.Now().Format(time.RFC3339))
		if !chClosed {
			close(fileTickCh)
			close(redisTickCh)
			chClosed = true
		}
		return
	}

	if !mktutil.IsValidMarketHrs(tick.ExchTS) {
		log.Printf("ExchTS: %s outside mkt hrs. Skip tick for Sym %s",
			tick.ExchTS.Format(time.RFC3339), instruments[tick.InstrumentToken].Sym)
		return
	}

	if !chClosed {
		fileTickCh <- tick
		redisTickCh <- tick
	}
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

	chClosed = false
	fileTickCh = make(chan *models.Tick, 5000)
	redisTickCh = make(chan *models.Tick, 5000)
	log.Println("File and Redis Channels created...")

	go handleFileTicks()
	go handleRedisTicks()
}

func onReconnect(attempt int, delay time.Duration) {
	log.Println("Reconnecting...")
}

func onError(err error) {
	log.Println("Error streaming ticks:", err)
}

func logTimeDiff(tick *kitemodels.Tick) {
	exchTS := tick.Timestamp.Time
	now := time.Now()
	diff := now.Sub(exchTS).Milliseconds()
	log.Printf("Sym: %s, ExchTS: %v, Now: %v, Diff: %d ms", instruments[tick.InstrumentToken].Sym, exchTS, now, diff)
}

func handleFileTicks() {
	f, err := createTickFile()
	if err != nil {
		log.Fatalln("Error creating ticker file: ", err)
	}
	defer f.Close()

	for {
		tick, ok := <-fileTickCh
		if !ok {
			log.Printf("File Tick Channel closed. Exiting handleFileTicks goroutine...")
			return
		}
		writeTickToCsv(tickFile, tick)
	}
}

func handleRedisTicks() {
	defer rdb.Close()
	for {
		tick, ok := <-redisTickCh
		if !ok {
			log.Printf("Redis Tick Channel closed. Exiting handleRedisTicks goroutine...")
			return
		}

		//start := time.Now()
		utils.WriteTickToRedis(ctx, rdb, tick)
		//end := time.Now()
	}

}

package ticker

import (
	"context"
	"fmt"
	"log"
	"time"

	kitemodels "github.com/zerodha/gokiteconnect/v4/models"
	kiteticker "github.com/zerodha/gokiteconnect/v4/ticker"
	utils "org.hbb/algo-trading/pkg/utils"
)

var (
	fileTickCh  chan *kitemodels.Tick
	redisTickCh chan *kitemodels.Tick
	chClosed    bool
)

func onTick(tick kitemodels.Tick) {
	//log.Println(getTickData(tick))
	// Close the channels 5 mins after market close
	if mktutil.IsAfterMarketHrs(time.Now().Add(5*time.Minute)) && !chClosed {
		log.Printf("Current Time: %s after mkt hrs. Closing File and Redis channels...",
			time.Now().Format(time.RFC3339))
		if !chClosed {
			close(fileTickCh)
			close(redisTickCh)
			chClosed = true
		}
		return
	}

	if !mktutil.IsValidMarketHrs(tick.Timestamp.Time) {
		log.Printf("ExchTS: %s outside mkt hrs. Skip tick for Sym %s",
			tick.Timestamp.Format(time.RFC3339), instruments[tick.InstrumentToken].Sym)
		return
	}

	if !chClosed {
		fileTickCh <- &tick
		redisTickCh <- &tick
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
	fileTickCh = make(chan *kitemodels.Tick, 5000)
	redisTickCh = make(chan *kitemodels.Tick, 5000)
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
		writeToCsv(tick)
	}
}

func handleRedisTicks() {
	rdb := utils.GetRedisClient()
	defer rdb.Close()
	ctx := context.Background()

	for {
		tick, ok := <-redisTickCh
		if !ok {
			log.Printf("Redis Tick Channel closed. Exiting handleRedisTicks goroutine...")
			return
		}

		start := time.Now()
		keyTS := tick.Timestamp.Time.Format("200601021504")
		keySym := instruments[tick.InstrumentToken].Sym

		ltpKey := fmt.Sprintf("LTP:ts:sym:%s:%s", keyTS, keySym)
		ltpValue := fmt.Sprintf("%f", tick.LastPrice)

		_, err := rdb.RPush(ctx, ltpKey, ltpValue).Result()
		if err != nil {
			log.Println("Failed pushing tick LTP to redis: ", err)
		}

		volKey := fmt.Sprintf("VOL:ts:sym:%s:%s", keyTS, keySym)
		volValue := fmt.Sprintf("%d", tick.VolumeTraded)

		_, err = rdb.Set(ctx, volKey, volValue, 0).Result()
		if err != nil {
			log.Println("Failed pushing tick VOL to redis: ", err)
		}

		end := time.Now()

		go func(s string) {
			log.Println(s)
		}(fmt.Sprintf("Completed redis processing in %f seconds for %s", end.Sub(start).Seconds(), keySym))
	}

}

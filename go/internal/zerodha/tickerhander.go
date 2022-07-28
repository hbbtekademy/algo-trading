package zerodha

import (
	"fmt"
	"github.com/go-redis/redis/v8"
	kiteconnect "github.com/zerodha/gokiteconnect/v4"
	"log"
	"os"
	"time"

	kitemodels "github.com/zerodha/gokiteconnect/v4/models"
	kiteticker "github.com/zerodha/gokiteconnect/v4/ticker"
	"org.hbb/algo-trading/go/models"
	redisutils "org.hbb/algo-trading/go/pkg/utils/redis"
)

var (
	fileTickChannel  chan *models.Tick
	redisTickChannel chan *models.Tick
	channelClosed    bool
)

const channelSize = 5000
const bufferTimeToCollectAfterMarketHoursTickData = -5 //Observed market tick data is received after market close. Buffer time need to collate these ticks.

func onTick(kiteTick kitemodels.Tick) {
	//log.Println(getTickData(tick))
	// Close the channels 5 mins after market close
	tick := mapKiteTickToCBTick(kiteTick)

	if marketSpecifications.IsAfterMarketHrs(getCurrentTimeWithBuffer()) && !channelClosed {
		log.Printf("Current Time: %s after mkt hrs. Closing File and Redis channels...",
			time.Now().Format(time.RFC3339))
		if !channelClosed {
			//Market Closed. Close all channels.
			close(fileTickChannel)
			close(redisTickChannel)
			channelClosed = true
		}
		return
	}

	if !marketSpecifications.IsMarketOpen(tick.ExchangeTS) {
		//Safety - Are we receiving ticks after close of market/
		log.Printf("ExchangeTS: %s outside mkt hrs. Skip tick for Sym %s",
			tick.ExchangeTS.Format(time.RFC3339), instruments[tick.InstrumentToken].Sym)
		return
	}

	if !channelClosed {
		fileTickChannel <- tick
		redisTickChannel <- tick
	}
}

func mapKiteTickToCBTick(kiteTick kitemodels.Tick) *models.Tick {
	cbTick := &models.Tick{
		InstrumentToken:    kiteTick.InstrumentToken,
		Sym:                instruments[kiteTick.InstrumentToken].Sym,
		ExchangeTS:         kiteTick.Timestamp.Time,
		LastTradeTS:        kiteTick.LastTradeTime.Time,
		LTP:                float32(kiteTick.LastPrice),
		LastTradedQuantity: kiteTick.LastTradedQuantity,
		VolumeTraded:       kiteTick.VolumeTraded,
	}
	return cbTick
}

func getCurrentTimeWithBuffer() time.Time {
	return time.Now().Add(bufferTimeToCollectAfterMarketHoursTickData * time.Minute)
}

func onConnect() {
	log.Println("Connected")

	err := kiteTickerClient.Subscribe(getInstrumentTokens())
	if err != nil {
		log.Fatalln(err)
	}

	err = kiteTickerClient.SetMode(kiteticker.ModeFull, getInstrumentTokens())
	if err != nil {
		log.Fatalln("Error setting Ticker Mode:", err)
	}
	log.Println("Tokens subscribed..")

	channelClosed = false
	// tick data is streamed to 2 destinations - one file and one redis. (TODO: Shirish - need to read this code deeper/ )

	fileTickChannel = make(chan *models.Tick, channelSize)
	redisTickChannel = make(chan *models.Tick, channelSize)
	log.Println("File and Redis Channels created...")

	go streamTicksToFile()
	go streamTicksToRedisDatabase()
}
func onReconnect(attempt int, delay time.Duration) {
	//TODO: future implementation - attempt int, delay time.Duration - provide a reconnect strategy
	log.Println("Reconnecting...")
}

func onError(err error) {
	log.Println("Error streaming ticks:", err)
}

// Triggered when websocket connection is closed
func onClose(code int, reason string) {
	fmt.Println("Close: ", code, reason)
}

// Triggered when maximum number of reconnect attempt is made and the program is terminated
func onNoReconnect(attempt int) {
	fmt.Printf("Maximum no of reconnect attempt reached: %d", attempt)
}

// Triggered when order update is received
func onOrderUpdate(order kiteconnect.Order) {
	fmt.Printf("Order: %s", order.OrderID)
}

func streamTicksToFile() {
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
		writeTickToCsvFile(tickDataFile, tick)
	}
}

func streamTicksToRedisDatabase() {
	defer func(redisClient *redis.Client) {
		err := redisClient.Close()
		if err != nil {
			log.Fatalln("Error closing redis client: ", err)
		}
	}(redisClient)
	for {
		tick, ok := <-redisTickChannel
		if !ok {
			log.Printf("Redis Tick Channel closed. Exiting streamTicksToRedisDatabase goroutine...")
			return
		}
		redisutils.WriteTickToRedis(ctx, redisClient, tick)
	}

}

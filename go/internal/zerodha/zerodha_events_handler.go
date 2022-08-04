package zerodha

import (
	"fmt"
	kiteConnect "github.com/zerodha/gokiteconnect/v4"
	kiteModels "github.com/zerodha/gokiteconnect/v4/models"
	kiteTicker "github.com/zerodha/gokiteconnect/v4/ticker"
	"log"
	"org.hbb/algo-trading/go/models"
	csvUtils "org.hbb/algo-trading/go/pkg/utils/csv"
	eventHandlerUtils "org.hbb/algo-trading/go/pkg/utils/event_handler"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
	"time"
)

var (
	fileTickChannel  chan *models.Tick
	redisTickChannel chan *models.Tick
	channelClosed    bool
)

const channelSize = 5000

func onTick(kiteTick kiteModels.Tick) {
	//log.Println(getTickData(tick))
	tick := mapKiteTickToCBTick(kiteTick)
	eventHandlerUtils.ConsumeTick(tick, marketSpecifications, channelClosed, fileTickChannel, redisTickChannel)
}

func mapKiteTickToCBTick(kiteTick kiteModels.Tick) *models.Tick {
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

func onConnect() {
	log.Println("Connected")

	err := kiteTickerClient.Subscribe(getInstrumentTokens())
	if err != nil {
		log.Fatalln("Error subscribing instrument tokens", err)
	}

	err = kiteTickerClient.SetMode(kiteTicker.ModeFull, getInstrumentTokens())
	if err != nil {
		log.Fatalln("Error setting Ticker Mode:", err)
	}
	log.Println("Tokens subscribed..")

	channelClosed = false
	fileTickChannel = make(chan *models.Tick, channelSize)
	redisTickChannel = make(chan *models.Tick, channelSize)
	log.Println("File and Redis Channels created...")

	go csvUtils.StreamTicksToFile(fileTickChannel, tickDataFile, instruments)
	go redisUtils.StreamTicksToRedisDatabase(redisClient, redisTickChannel, ctx)
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
func onOrderUpdate(order kiteConnect.Order) {
	fmt.Printf("Order: %s", order.OrderID)
}

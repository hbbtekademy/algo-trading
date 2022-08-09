package angel_one

import (
	"log"
	"strconv"
	"time"

	"org.hbb/algo-trading/go/models"
	csvUtils "org.hbb/algo-trading/go/pkg/utils/csv"
	eventHandlerUtils "org.hbb/algo-trading/go/pkg/utils/event_handler"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
)

var (
	fileTickChannel  chan *models.Tick
	redisTickChannel chan *models.Tick
	channelClosed    bool
)

const (
	channelSize        = 5000
	tk                 = "tk"
	ltt                = "ltt"
	ltp                = "ltp"
	ltq                = "ltq"
	v                  = "v"
	e                  = "e"
	angelOneTimeFormat = "02/01/2006 15:04:05"
)

// Triggered when a message is received
func onMessage(message []map[string]interface{}) {
	log.Printf("Message Received :- %v\n\n", message)
	for _, element := range message {
		if consumeMessage(element) {
			tick := mapAngelOneTickToCBTick(element)
			eventHandlerUtils.ConsumeTick(tick, marketSpecifications, channelClosed, fileTickChannel, redisTickChannel)
		}
	}
}

func consumeMessage(element map[string]interface{}) bool {
	return !isMessageTimeFeed(element)
}

func isMessageTimeFeed(element map[string]interface{}) bool {
	return element["name"] != nil && element["name"].(string) == "tm"
}

func mapAngelOneTickToCBTick(message map[string]interface{}) *models.Tick {
	//TODO: Convert message into cbTick. Per preliminary analysis, Angel One feed does not seem to provide any timestamps
	// Source : https://smartapi.angelbroking.com/docs/WebSocketStreaming
	instrumentToken := getInstrumentToken(message)
	symbol := getSymbol(message)
	exchangeTs := getExchangeTs(message)
	//TODO: need to find where is this timestamp on the message
	lastTradeTs := exchangeTs
	lastTradedPrice := getLastTradedPrice(message)
	lastTradedQuantity := getLastTradedQuantity(message)
	volume := getVolume(message)

	cbTick := &models.Tick{
		InstrumentToken:    uint32(instrumentToken),
		Sym:                symbol,
		ExchangeTS:         exchangeTs,
		LastTradeTS:        lastTradeTs,
		LTP:                float32(lastTradedPrice),
		LastTradedQuantity: uint32(lastTradedQuantity),
		VolumeTraded:       uint32(volume),
	}
	return cbTick
}

func getVolume(message map[string]interface{}) int64 {
	volume := int64(0)
	if message[v] != nil {
		volume, _ = strconv.ParseInt(message[v].(string), 10, 32)
	}
	return volume
}

func getLastTradedQuantity(message map[string]interface{}) int64 {
	lastTradedQuantity := int64(0)
	if message[ltq] != nil {
		lastTradedQuantity, _ = strconv.ParseInt(message[ltq].(string), 10, 32)
	}
	return lastTradedQuantity
}

func getLastTradedPrice(message map[string]interface{}) float64 {
	lastTradedPrice := float64(0)
	if message[ltp] != nil {
		lastTradedPrice, _ = strconv.ParseFloat(message[ltp].(string), 64)
	}
	return lastTradedPrice
}

func getExchangeTs(message map[string]interface{}) time.Time {
	exchangeTs := time.UnixMilli(0)
	if message[ltt] != nil {
		location, _ := time.LoadLocation("Asia/Kolkata")
		exchangeTs, _ = time.ParseInLocation(angelOneTimeFormat, message[ltt].(string), location)
	}
	return exchangeTs
}

func getSymbol(message map[string]interface{}) string {
	symbol := ""
	if message[e] != nil {
		symbol = message[e].(string)
	}
	return symbol
}

func getInstrumentToken(message map[string]interface{}) int64 {
	instrumentToken := int64(0)
	if message[tk] != nil {
		instrumentToken, _ = strconv.ParseInt(message[tk].(string), 10, 32)
	}
	return instrumentToken
}

// Triggered when any error is raised
func onError(err error) {
	log.Println("Error: ", err)
}

// Triggered when websocket connection is closed
func onClose(code int, reason string) {
	log.Println("Close: ", code, reason)
}

// Triggered when connection is established and ready to send and accept data
func onConnect() {
	log.Println("Connected")
	err := socketClient.Subscribe()
	if err != nil {
		log.Println("err: ", err)
	}
	channelClosed = false
	fileTickChannel = make(chan *models.Tick, channelSize)
	redisTickChannel = make(chan *models.Tick, channelSize)
	log.Println("File and Redis Channels created...")

	go csvUtils.StreamTicksToFile(fileTickChannel, instruments)
	go redisUtils.StreamTicksToRedisDatabase(redisClient, redisTickChannel, ctx)

}

// Triggered when reconnection is attempted which is enabled by default
func onReconnect(attempt int, delay time.Duration) {
	log.Printf("Reconnect attempt %d in %fs\n\n", attempt, delay.Seconds())
}

// Triggered when maximum number of reconnect attempt is made and the program is terminated
func onNoReconnect(attempt int) {
	log.Printf("Maximum no of reconnect attempt reached: %d\n\n", attempt)
}

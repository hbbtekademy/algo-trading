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
	angelOneTimeFormat = "02/01/2006 15:04:05"
)

// Triggered when a message is received
func onMessage(message []map[string]interface{}) {
	log.Printf("Message Received :- %v\n\n", message)
	for _, element := range message {
		tick := mapAngelOneTickToCBTick(element)
		eventHandlerUtils.ConsumeTick(tick, marketSpecifications, channelClosed, fileTickChannel, redisTickChannel)
	}

}

func mapAngelOneTickToCBTick(message map[string]interface{}) *models.Tick {
	//TODO: Convert message into cbTick. Per preliminary analysis, Angel One feed does not seem to provide any timestamps
	log.Printf("Message Received :- %v\n\n", message)
	// Source : https://smartapi.angelbroking.com/docs/WebSocketStreaming

	instrumentToken, _ := strconv.ParseInt(message[tk].(string), 10, 32)
	symbol := message["e"].(string)
	exchangeTs, _ := time.Parse(angelOneTimeFormat, message[ltt].(string))
	//TODO: Where is lastTradeTs
	//lastTradeTs, _ := time.Parse("2006-01-02 15:04:05", message["ltt"].(string))
	ltp, _ := strconv.ParseFloat(message[ltp].(string), 64)
	ltq, _ := strconv.ParseInt(message[ltq].(string), 10, 32)
	volume, _ := strconv.ParseInt(message[v].(string), 10, 32)

	cbTick := &models.Tick{
		InstrumentToken:    uint32(instrumentToken),
		Sym:                symbol,
		ExchangeTS:         exchangeTs,
		LastTradeTS:        exchangeTs, //TODO: need to find where is this timestamp on the message
		LTP:                float32(ltp),
		LastTradedQuantity: uint32(ltq),
		VolumeTraded:       uint32(volume),
	}
	return cbTick
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

	go csvUtils.StreamTicksToFile(fileTickChannel, tickDataFile, instruments)
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

package angel_one

import (
	"fmt"
	"github.com/angelbroking-github/smartapigo/websocket"
	"log"
	"org.hbb/algo-trading/go/models"
	csvUtils "org.hbb/algo-trading/go/pkg/utils/csv"
	eventHandlerUtils "org.hbb/algo-trading/go/pkg/utils/event_handler"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
	"time"
)

var (
	socketClient     *websocket.SocketClient
	fileTickChannel  chan *models.Tick
	redisTickChannel chan *models.Tick
	channelClosed    bool
)

const (
	channelSize = 5000
)

// Triggered when a message is received
func onMessage(message []map[string]interface{}) {
	fmt.Printf("Message Received :- %v\n", message)
	tick := mapAngelOneTickToCBTick(message)
	eventHandlerUtils.ConsumeTick(tick, marketSpecifications, channelClosed, fileTickChannel, redisTickChannel)
}

func mapAngelOneTickToCBTick(message []map[string]interface{}) *models.Tick {
	//TODO: Convert message into cbTick. Per preliminary analysis, Angel One feed does not seem to provide any timestamps
	cbTick := &models.Tick{
		InstrumentToken:    0,
		Sym:                "string",
		ExchangeTS:         time.Now(),
		LastTradeTS:        time.Now(),
		LTP:                0,
		LastTradedQuantity: 0,
		VolumeTraded:       0,
	}
	return cbTick
}

// Triggered when any error is raised
func onError(err error) {
	fmt.Println("Error: ", err)
}

// Triggered when websocket connection is closed
func onClose(code int, reason string) {
	fmt.Println("Close: ", code, reason)
}

// Triggered when connection is established and ready to send and accept data
func onConnect() {
	fmt.Println("Connected")
	err := socketClient.Subscribe()
	if err != nil {
		fmt.Println("err: ", err)
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
	fmt.Printf("Reconnect attempt %d in %fs\n", attempt, delay.Seconds())
}

// Triggered when maximum number of reconnect attempt is made and the program is terminated
func onNoReconnect(attempt int) {
	fmt.Printf("Maximum no of reconnect attempt reached: %d\n", attempt)
}

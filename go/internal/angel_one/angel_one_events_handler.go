package angel_one

import (
	"encoding/csv"
	"fmt"
	"github.com/angelbroking-github/smartapigo/websocket"
	"github.com/go-redis/redis/v8"
	"log"
	"org.hbb/algo-trading/go/models"
	redisutils "org.hbb/algo-trading/go/pkg/utils/redis"
	"os"
	"time"
)

var (
	socketClient     *websocket.SocketClient
	fileTickChannel  chan *models.Tick
	redisTickChannel chan *models.Tick
	channelClosed    bool
	tick             *models.Tick
)

//Observed market tick data is received after market close. Buffer time need to collate these ticks.
const (
	bufferTimeToCollectAfterMarketHoursTickData = -5
	channelSize                                 = 5000
)

// Triggered when a message is received
func onMessage(message []map[string]interface{}) {
	fmt.Printf("Message Received :- %v\n", message)
	tick := mapAngelOneTickToCBTick(message)

	// Close the channels 5 minutes after market close
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

func getCurrentTimeWithBuffer() time.Time {
	return time.Now().Add(bufferTimeToCollectAfterMarketHoursTickData * time.Minute)
}

func mapAngelOneTickToCBTick(message []map[string]interface{}) *models.Tick {
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

	go streamTicksToFile()
	go streamTicksToRedisDatabase()

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

func createTickFile() (*os.File, error) {
	var err error
	y, m, d := time.Now().Date()
	fn := fmt.Sprintf("Ticker-%d%d%d.csv", y, int(m), d)

	tickDataFile, err = os.OpenFile(fn, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Println("Error opening zerodha file:", err)
	}

	log.Printf("Tick file %s created...", fn)

	return tickDataFile, err
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

func writeTickToCsvFile(f *os.File, tick *models.Tick) {
	w := csv.NewWriter(f)
	defer w.Flush()

	err := w.Write(getTickData(tick))
	if err != nil {
		log.Fatalln("Error writing to zerodha file:", err)
	}
}

func getTickData(tick *models.Tick) []string {
	return []string{
		instruments[tick.InstrumentToken].Sym,
		tick.ExchangeTS.Format(time.RFC3339),
		tick.LastTradeTS.Format(time.RFC3339),
		fmt.Sprintf("%f", tick.LTP),
		fmt.Sprintf("%d", tick.LastTradedQuantity),
		fmt.Sprintf("%d", tick.VolumeTraded),
	}
}

// Triggered when reconnection is attempted which is enabled by default
func onReconnect(attempt int, delay time.Duration) {
	fmt.Printf("Reconnect attempt %d in %fs\n", attempt, delay.Seconds())
}

// Triggered when maximum number of reconnect attempt is made and the program is terminated
func onNoReconnect(attempt int) {
	fmt.Printf("Maximum no of reconnect attempt reached: %d\n", attempt)
}

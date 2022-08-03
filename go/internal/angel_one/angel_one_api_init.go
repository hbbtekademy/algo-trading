package angel_one

import (
	"context"
	"fmt"
	SmartApi "github.com/angelbroking-github/smartapigo"
	"github.com/angelbroking-github/smartapigo/websocket"
	"github.com/go-redis/redis/v8"
	"log"
	"org.hbb/algo-trading/go/models"
	"org.hbb/algo-trading/go/pkg/utils"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
	"os"
	"time"
)

var (
	tickDataFile                   *os.File
	redisClient                    *redis.Client
	ctx                            context.Context
	marketStartTime, marketEndTime time.Time
	instruments                    models.Instruments
	marketSpecifications           *utils.MarketSpecifications
)

const (
	AngelOneClientCode string = "123123asd"
	AngelOnePassword   string = "123asdasd"
	AngelOneApiKey     string = "apikey"
)

func Start() {

	initMarketSpecification() // market data - all - tick-consumer / tick-adapter // this is a tick data consumer
	initInstruments()
	initRedisClient()

	// Create New Angel Broking Client
	SmartApiClient := SmartApi.New(AngelOneClientCode, AngelOnePassword, AngelOneApiKey)

	// User Login and Generate User Session
	session, err := SmartApiClient.GenerateSession()

	if err != nil {
		fmt.Println(err.Error())
		return
	}

	//Get User Profile
	session.UserProfile, err = SmartApiClient.GetUserProfile()

	if err != nil {
		fmt.Println(err.Error())
		return
	}

	// New Websocket Client
	socketClient := websocket.New(session.ClientCode, session.FeedToken, "nse_cm|17963&nse_cm|3499&nse_cm|11536&nse_cm|21808&nse_cm|317")

	// Assign callbacks
	socketClient.OnError(onError)
	socketClient.OnClose(onClose)
	socketClient.OnMessage(onMessage)
	socketClient.OnConnect(onConnect)
	socketClient.OnReconnect(onReconnect)
	socketClient.OnNoReconnect(onNoReconnect)

	// Start Consuming Data
	socketClient.Serve()
}

func initRedisClient() {
	ctx = context.Background()
	redisClient = redisUtils.GetRTRedisClient()
}

func initInstruments() {
	//instruments := GetAllAngleOneInstruments()
}

func initMarketSpecification() {
	marketStartTime, marketEndTime = utils.GetMarketTime()
	marketSpecifications = utils.GetMarketSpecs(marketStartTime, marketEndTime)
	log.Printf("Mkt Start Time: %v, Mkt End time: %v", marketStartTime, marketEndTime)
}

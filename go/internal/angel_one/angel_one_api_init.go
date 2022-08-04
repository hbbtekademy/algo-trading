package angel_one

import (
	"context"
	"fmt"
	SmartApi "github.com/angelbroking-github/smartapigo"
	"github.com/angelbroking-github/smartapigo/websocket"
	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/go/models"
	marketUtils "org.hbb/algo-trading/go/pkg/utils/market"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
	"os"
)

var (
	tickDataFile         *os.File
	redisClient          *redis.Client
	ctx                  context.Context
	instruments          models.Instruments
	marketSpecifications *marketUtils.Specifications
)

const (
	AngelOneClientCode string = "123123asd"
	AngelOnePassword   string = "123asdasd"
	AngelOneApiKey     string = "apikey"
)

func Start() {

	ctx, redisClient = redisUtils.InitRedisClient()
	marketSpecifications = marketUtils.InitMarketSpecification() // market data - all - tick-consumer / tick-adapter // this is a tick data consumer
	initInstruments()

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

func initInstruments() {
	//instruments := GetAllAngleOneInstruments()
}

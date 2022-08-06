package angel_one

import (
	"context"
	"fmt"
	SmartApi "github.com/angelbroking-github/smartapigo"
	"github.com/angelbroking-github/smartapigo/websocket"
	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/go/models"
	envutils "org.hbb/algo-trading/go/pkg/utils/env"
	marketUtils "org.hbb/algo-trading/go/pkg/utils/market"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
	"os"
)

var (
	tickDataFile         *os.File
	redisClient          *redis.Client
	ctx                  context.Context
	instruments          models.Instruments
	marketSpecifications *models.Specifications
	socketClient         *websocket.SocketClient
)

func Start() {

	angelOneClientCode := envutils.MustGetEnv("ANGEL_ONE_CLIENT_CODE")
	angelOnePassword := envutils.MustGetEnv("ANGEL_ONE_PASSWORD")
	angelOneApiKey := envutils.MustGetEnv("ANGEL_ONE_API_KEY")

	ctx, redisClient = redisUtils.InitRedisClient()
	marketSpecifications = marketUtils.InitMarketSpecification() // market data - all - tick-consumer / tick-adapter // this is a tick data consumer
	initInstruments()

	// Create New Angel Broking Client
	SmartApiClient := SmartApi.New(angelOneClientCode, angelOnePassword, angelOneApiKey)

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
	//TODO: scrips should be provided as input.
	socketClient = websocket.New(session.ClientCode, session.FeedToken, "nse_cm|1594")

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

package zerodha

import (
	"context"
	"log"
	instrumentsRepository "org.hbb/algo-trading/go/pkg/instruments-repository"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
	"os"
	"time"

	"github.com/go-redis/redis/v8"
	kiteTicker "github.com/zerodha/gokiteconnect/v4/ticker"
	"org.hbb/algo-trading/go/models"
	secretManager "org.hbb/algo-trading/go/pkg/secret-manager"
	"org.hbb/algo-trading/go/pkg/utils"
)

var (
	kiteTickerClient               *kiteTicker.Ticker
	tickDataFile                   *os.File
	redisClient                    *redis.Client
	ctx                            context.Context
	marketStartTime, marketEndTime time.Time
	instruments                    models.Instruments
	marketSpecifications           *utils.MarketSpecifications
)

func Start() {
	initMarketSpecification() // market data - all - tick-consumer / tick-adapter // this is a tick data consumer
	initInstruments()
	initRedisClient()

	apiKey := secretManager.GetSecret(secretManager.KiteApiKeySK)
	accessToken := secretManager.GetSecret(secretManager.KiteAccessTokenSK)

	kiteTickerClient = kiteTicker.New(apiKey, accessToken)

	// Assign callbacks
	kiteTickerClient.OnError(onError)
	kiteTickerClient.OnClose(onClose)
	kiteTickerClient.OnConnect(onConnect) //instrument supplied via onConnect
	kiteTickerClient.OnReconnect(onReconnect)
	kiteTickerClient.OnNoReconnect(onNoReconnect)
	kiteTickerClient.OnTick(onTick)
	kiteTickerClient.OnOrderUpdate(onOrderUpdate)

	//Start the connection
	kiteTickerClient.Serve() //blocking call. At this point, the ticks start coming in.
}

func initInstruments() {
	instruments = instrumentsRepository.GetNiftyFutInstruments()
}

func initRedisClient() {
	ctx = context.Background()
	redisClient = redisUtils.GetRTRedisClient()
}

func initMarketSpecification() {
	marketStartTime, marketEndTime = utils.GetMarketTime()
	marketSpecifications = utils.GetMarketSpecs(marketStartTime, marketEndTime)
	log.Printf("Mkt Start Time: %v, Mkt End time: %v", marketStartTime, marketEndTime)
}

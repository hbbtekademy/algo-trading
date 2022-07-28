package ticker

import (
	"context"
	"log"
	instrumentsRepository "org.hbb/algo-trading/go/pkg/instruments-repository"
	"os"
	"time"

	"github.com/go-redis/redis/v8"
	kiteTicker "github.com/zerodha/gokiteconnect/v4/ticker"
	"org.hbb/algo-trading/go/models"
	secretManager "org.hbb/algo-trading/go/pkg/secret-manager"
	utils "org.hbb/algo-trading/go/pkg/utils"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
)

var (
	ticker                         *kiteTicker.Ticker
	tickFile                       *os.File
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

	ticker = kiteTicker.New(apiKey, accessToken)
	ticker.OnConnect(onConnect)
	ticker.OnTick(onTick)
	ticker.OnError(onError)
	ticker.OnReconnect(onReconnect)
	ticker.Serve() //blocking call. At this point, the ticks start coming in.
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

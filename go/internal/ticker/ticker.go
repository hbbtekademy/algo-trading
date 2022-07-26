package ticker

import (
	"context"
	"log"
	"os"
	"time"

	"github.com/go-redis/redis/v8"
	kiteticker "github.com/zerodha/gokiteconnect/v4/ticker"
	"org.hbb/algo-trading/go/models"
	instmanager "org.hbb/algo-trading/go/pkg/instrument-manager"
	secretmanager "org.hbb/algo-trading/go/pkg/secret-manager"
	utils "org.hbb/algo-trading/go/pkg/utils"
	redisutils "org.hbb/algo-trading/go/pkg/utils/redis"
)

var (
	ticker      *kiteticker.Ticker
	tickFile    *os.File
	rdb         *redis.Client
	ctx         context.Context
	mst, met    time.Time
	instruments models.Instruments
	mktutil     *utils.MarketSpecifications
)

func Start() {
	initVars() // market data - all - tick-consumer / tick-adapter // this is a tick data consumer
	initRedisClient()

	apiKey := secretmanager.GetSecret(secretmanager.KiteApiKeySK)
	accessToken := secretmanager.GetSecret(secretmanager.KiteAccessTokenSK)

	ticker = kiteticker.New(apiKey, accessToken)
	ticker.OnConnect(onConnect)
	ticker.OnTick(onTick)
	ticker.OnError(onError)
	ticker.OnReconnect(onReconnect)
	ticker.Serve() //blocking call. At this point, the ticks start coming in.
}

func initRedisClient() {
	ctx = context.Background()
	rdb = redisutils.GetRTRedisClient()
}

func initVars() {
	mst, met = utils.GetMarketTime()
	mktutil = utils.GetMarketSpecs(mst, met)
	log.Printf("Mkt Start Time: %v, Mkt End time: %v", mst, met)
	instruments = instmanager.GetNiftyFutInstruments()
}

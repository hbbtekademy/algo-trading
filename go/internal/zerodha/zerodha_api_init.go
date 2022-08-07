package zerodha

import (
	"context"
	"os"

	"github.com/go-redis/redis/v8"
	kiteTicker "github.com/zerodha/gokiteconnect/v4/ticker"
	"org.hbb/algo-trading/go/models"
	instrumentsRepository "org.hbb/algo-trading/go/pkg/instruments-repository"
	secretManager "org.hbb/algo-trading/go/pkg/secret-manager"
	marketUtils "org.hbb/algo-trading/go/pkg/utils/market"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
)

var (
	kiteTickerClient     *kiteTicker.Ticker
	tickDataFile         *os.File
	redisClient          *redis.Client
	ctx                  context.Context
	instruments          models.Instruments
	marketSpecifications *models.Specifications
)

func Start() {

	ctx, redisClient = redisUtils.InitRedisClient()
	marketSpecifications = marketUtils.InitMarketSpecification()
	initInstruments()

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

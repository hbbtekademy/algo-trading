package zerodha

import (
	"context"
	"os"

	"github.com/go-redis/redis/v8"
	kiteTicker "github.com/zerodha/gokiteconnect/v4/ticker"
	"org.hbb/algo-trading/go/models"
	marketUtils "org.hbb/algo-trading/go/pkg/repository/config"
	instrumentsRepository "org.hbb/algo-trading/go/pkg/repository/instruments"
	redisUtils "org.hbb/algo-trading/go/pkg/repository/marketdata"
	secretManager "org.hbb/algo-trading/go/pkg/secret-manager"
)

var (
	kiteTickerClient     *kiteTicker.Ticker
	tickDataFile         *os.File
	redisClient          *redis.Client
	ctx                  context.Context
	instruments          models.Instruments
	marketSpecifications *models.MarketSpecifications
)

func Start() {

	ctx, redisClient = redisUtils.InitRealTimeRedisClient()
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

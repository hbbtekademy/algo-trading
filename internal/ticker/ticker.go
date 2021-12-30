package ticker

import (
	"log"
	"os"
	"time"

	kiteticker "github.com/zerodha/gokiteconnect/v4/ticker"
	"org.hbb/algo-trading/models"
	instmanager "org.hbb/algo-trading/pkg/instrument-manager"
	secretmanager "org.hbb/algo-trading/pkg/secret-manager"
	utils "org.hbb/algo-trading/pkg/utils"
)

var (
	ticker      *kiteticker.Ticker
	tickFile    *os.File
	mst, met    time.Time
	instruments models.Instruments
	mktutil     *utils.Mktutil
)

func Start() {
	initVars()

	apiKey := secretmanager.GetSecret(secretmanager.KiteApiKeySK)
	accessToken := secretmanager.GetSecret(secretmanager.KiteAccessTokenSK)

	ticker = kiteticker.New(apiKey, accessToken)
	ticker.OnTick(onTick)
	ticker.OnConnect(onConnect)
	ticker.OnReconnect(onReconnect)
	ticker.OnError(onError)
	ticker.Serve()
}

func initVars() {
	mst, met = utils.GetMarketTime()
	mktutil = utils.NewMktUtil(mst, met)
	log.Printf("Mkt Start Time: %v, Mkt End time: %v", mst, met)
	instruments = instmanager.GetNifty100()
	futNFOInsts := instmanager.GetNFOFut()
	for k, v := range futNFOInsts {
		instruments[k] = v
	}
}

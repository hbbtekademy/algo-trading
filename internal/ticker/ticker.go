package ticker

import (
	"log"
	"os"
	"time"

	kiteticker "github.com/zerodha/gokiteconnect/v4/ticker"
	secretmanager "org.hbb/algo-trading/pkg/secret-manager"
)

var (
	ticker   *kiteticker.Ticker
	tickFile *os.File

	mst, met time.Time
)

func Start() {
	mst, met = getMarketTime()
	log.Printf("Mkt Start Time: %v, Mkt End time: %v", mst, met)

	apiKey := secretmanager.GetSecret(secretmanager.KiteApiKeySK)
	accessToken := secretmanager.GetSecret(secretmanager.KiteAccessTokenSK)

	ticker = kiteticker.New(apiKey, accessToken)
	ticker.OnTick(onTick)
	ticker.OnConnect(onConnect)
	ticker.OnReconnect(onReconnect)
	ticker.OnError(onError)
	ticker.Serve()
}

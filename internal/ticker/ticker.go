package ticker

import (
	"fmt"
	"log"
	"os"
	"time"

	kiteticker "github.com/zerodha/gokiteconnect/v4/ticker"
	"org.hbb/algo-trading/models"
	instmanager "org.hbb/algo-trading/pkg/instrument-manager"
	secretmanager "org.hbb/algo-trading/pkg/secret-manager"
)

var (
	ticker      *kiteticker.Ticker
	tickFile    *os.File
	mst, met    time.Time
	instruments models.Instruments
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
	initMarketTime()
	log.Printf("Mkt Start Time: %v, Mkt End time: %v", mst, met)
	instruments = instmanager.GetNifty100()
	futNFOInsts := instmanager.GetNFOFut()
	for k, v := range futNFOInsts {
		instruments[k] = v
	}
}

func initMarketTime() {
	var err error
	y, m, d := time.Now().Date()
	mst, err = time.Parse(time.RFC3339, fmt.Sprintf("%d-%d-%dT08:59:59+05:30", y, int(m), d))
	if err != nil {
		log.Fatalln("failed getting market start time:", err)
	}

	met, err = time.Parse(time.RFC3339, fmt.Sprintf("%d-%d-%dT16:01:00+05:30", y, int(m), d))
	if err != nil {
		log.Fatalln("failed getting market end time:", err)
	}
}

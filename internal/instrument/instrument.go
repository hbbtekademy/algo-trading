package instrument

import (
	"log"

	kiteconnect "github.com/zerodha/gokiteconnect/v4"
	secretmanager "org.hbb/algo-trading/pkg/secret-manager"
)

var (
	kc *kiteconnect.Client
)

func GetKiteInstruments() kiteconnect.Instruments {
	apiKey := secretmanager.GetSecret(secretmanager.KiteApiKeySK)
	accessToken := secretmanager.GetSecret(secretmanager.KiteAccessTokenSK)

	kc = kiteconnect.New(apiKey)
	kc.SetAccessToken(accessToken)

	instruments, err := kc.GetInstruments()
	if err != nil {
		log.Fatalln("Failed getting instruments:", err)
	}

	return instruments
}

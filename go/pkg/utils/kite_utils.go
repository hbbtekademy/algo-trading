package utils

import (
	kiteconnect "github.com/zerodha/gokiteconnect/v4"
	secretmanager "org.hbb/algo-trading/go/pkg/secret-manager"
)

func GetKiteClient() *kiteconnect.Client {
	apiKey := secretmanager.GetSecret(secretmanager.KiteApiKeySK)
	accessToken := secretmanager.GetSecret(secretmanager.KiteAccessTokenSK)

	kc := kiteconnect.New(apiKey)
	kc.SetAccessToken(accessToken)

	return kc
}

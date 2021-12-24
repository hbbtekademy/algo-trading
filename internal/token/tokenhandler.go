package tokenservice

import (
	"fmt"
	"log"
	"net/http"

	kiteconnect "github.com/zerodha/gokiteconnect/v4"
	secretmanager "org.hbb/algo-trading/pkg/secret-manager"
)

func tokenHandler(w http.ResponseWriter, r *http.Request) {
	requestToken = r.URL.Query()["request_token"][0]
	log.Println("request token", requestToken)

	apiKey := secretmanager.GetSecret(secretmanager.KiteApiKeySK)
	apiSecret := secretmanager.GetSecret(secretmanager.KiteApiSecretSK)

	// Get user details and access token
	kc := kiteconnect.New(apiKey)

	log.Println("Got API Key and request token. Generating Access Token...")
	data, err := kc.GenerateSession(requestToken, apiSecret)
	if err != nil {
		log.Println("Error getting Access Token:", err)
		fmt.Fprintf(w, "Error: %v", err)
		return
	}

	log.Println("Got Access Token. Generating Access Token Secret...")
	err = secretmanager.CreateSecret(secretmanager.KiteAccessTokenSK, data.AccessToken)
	if err != nil {
		log.Println("Failed creating Acces Token Secret:", err)
		fmt.Fprintf(w, "Failed creating Access Token secret: %v", err)
		return
	}

	fmt.Fprint(w, "Successfully created Access Token secret...")
}

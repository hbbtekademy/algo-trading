package tokenservice

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	kiteconnect "github.com/zerodha/gokiteconnect/v4"
	secretmanager "org.hbb/algo-trading/go/pkg/secret-manager"
	envutils "org.hbb/algo-trading/go/pkg/utils/env"
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
		log.Println("Failed creating Access Token Secret:", err)
		fmt.Fprintf(w, "Failed creating Access Token secret: %v", err)
		return
	}

	fmt.Fprint(w, "Successfully created Access Token secret...")
}

func localTokenHandler(w http.ResponseWriter, r *http.Request) {
	requestToken = r.URL.Query()["request_token"][0]

	log.Println("request token", requestToken)

	apiKey := envutils.MustGetEnv("KITE_API_KEY")
	apiSecret := envutils.MustGetEnv("KITE_API_SECRET")

	// Get user details and access token
	kc := kiteconnect.New(apiKey)

	log.Println("Got API Key and request token. Generating Access Token...")
	data, err := kc.GenerateSession(requestToken, apiSecret)
	if err != nil {
		log.Println("Error getting Access Token:", err)
		fmt.Fprintf(w, "Error: %v", err)
		return
	}

	log.Printf("Got Access Token. Generating Access Token: %s", data.AccessToken)

	fmt.Fprint(w, "Successfully created Access Token secret...")
}

func localBreezeTokenHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		return
	}

	reqBody, _ := ioutil.ReadAll(r.Body)
	log.Println("URL Query Params: ", string(reqBody))
	apiSession = ""
	fmt.Fprint(w, "Successfully retrieved API Session...")
}

func localSensorData(w http.ResponseWriter, r *http.Request) {
	temp := r.URL.Query()["temp"][0]
	log.Println("Temp: ", temp)
	fmt.Fprint(w, "Successfully logged Temperature.")
}

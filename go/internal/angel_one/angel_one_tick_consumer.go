package angel_one

import (
	"fmt"
	SmartApi "github.com/angelbroking-github/smartapigo"
	"github.com/angelbroking-github/smartapigo/websocket"
)

const (
	AngelOneClientCode string = "123123asd"
	AngelOnePassword   string = "123asdasd"
	AngelOneApiKey     string = "apikey"
)

func Start() {
	// Create New Angel Broking Client
	SmartApiClient := SmartApi.New(AngelOneClientCode, AngelOnePassword, AngelOneApiKey)

	// User Login and Generate User Session
	session, err := SmartApiClient.GenerateSession()

	if err != nil {
		fmt.Println(err.Error())
		return
	}

	//Get User Profile
	session.UserProfile, err = SmartApiClient.GetUserProfile()

	if err != nil {
		fmt.Println(err.Error())
		return
	}

	// New Websocket Client
	socketClient := websocket.New(session.ClientCode, session.FeedToken, "nse_cm|17963&nse_cm|3499&nse_cm|11536&nse_cm|21808&nse_cm|317")

	// Assign callbacks
	socketClient.OnError(onError)
	socketClient.OnClose(onClose)
	socketClient.OnMessage(onMessage)
	socketClient.OnConnect(onConnect)
	socketClient.OnReconnect(onReconnect)
	socketClient.OnNoReconnect(onNoReconnect)

	// Start Consuming Data
	socketClient.Serve()
}

package angel_one

import (
	"context"
	"net/http"

	SmartApi "github.com/angelbroking-github/smartapigo"
	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/go/models"
	redisUtils "org.hbb/algo-trading/go/pkg/repository/marketdata"
	envUtils "org.hbb/algo-trading/go/pkg/utils/env"
)

var (
	redisClient *redis.Client
	ctx         context.Context
	instruments models.Instruments
)

func Start() {

	angelOneClientCode := envUtils.MustGetEnv("ANGEL_ONE_CLIENT_CODE")
	angelOnePassword := envUtils.MustGetEnv("ANGEL_ONE_PASSWORD")
	angelOneApiKey := envUtils.MustGetEnv("ANGEL_ONE_API_KEY")

	ctx, redisClient = redisUtils.InitRealTimeRedisClient()

	client := SmartApi.New(angelOneClientCode, angelOnePassword, angelOneApiKey)
	client.GenerateSession()

	// construct url values
	params := make(map[string]interface{})
	params["clientcode"] = angelOneClientCode
	params["password"] = angelOnePassword

	err := client.doEnvelope(http.MethodPost, "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByPassword", params, nil, &session)
	// Set accessToken on successful session retrieve
	if err == nil && session.AccessToken != "" {
		c.SetAccessToken(session.AccessToken)
	}

}

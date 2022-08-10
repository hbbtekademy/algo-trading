package redisutils

import (
	"context"
	"log"
	"testing"
	"time"

	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/go/models"
)

var (
	redisClient *redis.Client
	ctx         context.Context
)

func TestWriteTickToRedis(t *testing.T) {
	t.Parallel()

	ctx, redisClient = InitRedisClient()
	tick := getCBTick()

	WriteTickToRedis(ctx, redisClient, tick)
	statusCommand := redisClient.Ping(ctx)
	log.Print("status command: ", statusCommand.String())
	result, _ := redisClient.Set(ctx, "myKey1", time.Now(), 0).Result()
	log.Print("result", result)
	resultValue, _ := redisClient.Get(ctx, "myKey1").Result()
	log.Print("resultValue: ", resultValue)
}

func getCBTick() *models.Tick {
	cbTick := &models.Tick{
		InstrumentToken:    1234,
		Sym:                "symbol",
		ExchangeTS:         time.Now(),
		LastTradeTS:        time.Now(),
		LTP:                100.11,
		LastTradedQuantity: 200,
		VolumeTraded:       300,
	}
	return cbTick
}

package marketdata

import (
	"context"
	"log"

	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/go/models"
)

func StreamTicksToRedisDatabase(redisClient *redis.Client, redisTickChannel chan *models.Tick, ctx context.Context) {
	defer func(redisClient *redis.Client) {
		err := redisClient.Close()
		if err != nil {
			log.Fatalln("Error closing redis client: ", err)
		}
	}(redisClient)
	for {
		tick, ok := <-redisTickChannel
		if !ok {
			log.Printf("Redis Tick Channel closed. Exiting streamTicksToRedisDatabase goroutine...")
			return
		}
		WriteTickToRedis(ctx, redisClient, tick)
	}

}

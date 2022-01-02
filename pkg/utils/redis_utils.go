package utils

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/models"
)

func GetRedisClient() *redis.Client {
	host := MustGetEnv("REDIS_HOST")
	port := MustGetEnv("REDIS_PORT")
	rdb := redis.NewClient(&redis.Options{
		Addr:        fmt.Sprintf("%s:%s", host, port),
		Password:    "",
		DB:          0,
		DialTimeout: 250 * time.Millisecond,
	})

	connected := false
	for i := 0; i <= 10; i++ {
		_, err := rdb.Ping(context.Background()).Result()
		if err == nil {
			log.Println("Connection to redis server established...")
			connected = true
			break
		} else {
			log.Println("Failed connecting to redis client. Retrying: ", err)
			time.Sleep(5 * time.Second)
		}
	}

	if !connected {
		log.Fatalf("Unable to connect to Redis server at %s:%s. Exiting...", host, port)
	}

	return rdb
}

func WriteTickToRedis(ctx context.Context, rdb *redis.Client, tick *models.Tick) {
	keyTS := tick.ExchTS.Format("200601021504")
	keySym := tick.InstrumentToken

	ltpKey := fmt.Sprintf("LTP:ts:sym:%s:%d", keyTS, keySym)
	ltpValue := fmt.Sprintf("%f", tick.LTP)

	_, err := rdb.RPush(ctx, ltpKey, ltpValue).Result()
	if err != nil {
		log.Println("Failed pushing tick LTP to redis: ", err)
	}

	volKey := fmt.Sprintf("VOL:ts:sym:%s:%d", keyTS, keySym)
	volValue := fmt.Sprintf("%d", tick.VolumeTraded)

	_, err = rdb.Set(ctx, volKey, volValue, 0).Result()
	if err != nil {
		log.Println("Failed setting tick VOL to redis: ", err)
	}
}

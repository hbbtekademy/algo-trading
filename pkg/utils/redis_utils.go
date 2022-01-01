package utils

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/go-redis/redis/v8"
)

func GetRedisClient(ip string, port string) *redis.Client {
	rdb := redis.NewClient(&redis.Options{
		Addr:        fmt.Sprintf("%s:%s", ip, port),
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
		log.Fatalf("Unable to connect to Redis server at %s:%s. Exiting...", ip, port)
	}

	return rdb
}

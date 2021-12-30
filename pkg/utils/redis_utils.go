package utils

import (
	"time"

	"github.com/go-redis/redis/v8"
)

func GetRedisClient() *redis.Client {
	return redis.NewClient(&redis.Options{
		Addr:        "10.160.0.3:6379",
		Password:    "",
		DB:          0,
		DialTimeout: 1 * time.Second,
	})
}

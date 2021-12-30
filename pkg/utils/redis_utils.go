package utils

import (
	"fmt"
	"time"

	"github.com/go-redis/redis/v8"
)

func GetRedisClient(ip string, port string) *redis.Client {
	return redis.NewClient(&redis.Options{
		Addr:        fmt.Sprintf("%s:%s", ip, port),
		Password:    "",
		DB:          0,
		DialTimeout: 1 * time.Second,
	})
}

package main

import (
	"context"
	"github.com/go-redis/redis/v8"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
)

var (
	redisClient *redis.Client
	ctx         context.Context
)

const (
	// RedisTelegramChannel To test on local, ensure you have created the below channel on Redis
	RedisTelegramChannel string = "Smash-Telegram-Channel"
	TestMessage          string = "TEST-FromRedisChannel: Revise SL for TCS 6100 CE at 93.90"
)

func main() {
	initRedisClient()
	redisClient.Publish(ctx, RedisTelegramChannel, TestMessage)
}

func initRedisClient() {
	ctx = context.Background()
	redisClient = redisUtils.GetRTRedisClient()
}

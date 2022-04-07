package main

import (
	"context"
	"fmt"
	"log"
	"time"

	redistypes "org.hbb/algo-trading/pkg/redis/types"
	redisutils "org.hbb/algo-trading/pkg/utils/redis"
)

func main() {
	ctx := context.Background()
	rdb := redisutils.GetRTRedisClient()

	idxKey := redistypes.NewIdxKey(13278466)

	fmt.Println(idxKey.GetCS1MIdxKey())

	candleKeys, err := rdb.ZRange(ctx, idxKey.GetCS1MIdxKey(), 0, -1).Result()
	if err != nil {
		log.Fatal("Failed getting candlesticks from index", err)
	}

	fmt.Println("Date,Open,High,Low,Close,Volume")
	for _, key := range candleKeys {
		redisKey := redistypes.ParseKey(key)
		ohlcv, _ := redisutils.GetOHLCV(ctx, rdb, key)
		fmt.Printf("%s,%f,%f,%f,%f,%d\n", redisKey.TS.Format(time.RFC3339), ohlcv.Open, ohlcv.High, ohlcv.Low, ohlcv.Close, ohlcv.Volume)
	}

}

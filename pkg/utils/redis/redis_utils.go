package redisutils

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"sync"
	"time"

	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/models"
	redistypes "org.hbb/algo-trading/pkg/redis/types"
	"org.hbb/algo-trading/pkg/utils"
)

const (
	REDIS_HIST_DB = iota
	REDIS_RT_DB
	REDIS_SIG_DB
)

func GetHistRedisClient() *redis.Client {
	host := utils.MustGetEnv("REDIS_HIST_HOST")
	port := utils.MustGetEnv("REDIS_HIST_PORT")
	return getRedisClient(host, port, REDIS_HIST_DB)
}

func GetRTRedisClient() *redis.Client {
	host := utils.MustGetEnv("REDIS_RT_HOST")
	port := utils.MustGetEnv("REDIS_RT_PORT")
	return getRedisClient(host, port, REDIS_RT_DB)
}

func getRedisClient(host string, port string, redisdb int) *redis.Client {
	rdb := redis.NewClient(&redis.Options{
		Addr:        fmt.Sprintf("%s:%s", host, port),
		Password:    "",
		DB:          redisdb,
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
	key := redistypes.NewKey(tick.ExchTS, tick.InstrumentToken)
	idxKey := redistypes.NewIdxKey(tick.InstrumentToken)
	ltpValue := fmt.Sprintf("%f", tick.LTP)
	volValue := fmt.Sprintf("%d", tick.VolumeTraded)

	_, err := rdb.RPush(ctx, key.GetLTPKey(), ltpValue).Result()
	if err != nil {
		log.Println("Failed pushing tick LTP to redis: ", err)
	}

	_, err = rdb.Set(ctx, key.GetVOLKey(), volValue, 0).Result()
	if err != nil {
		log.Println("Failed setting tick VOL to redis: ", err)
	}

	_, err = rdb.ZAdd(ctx, idxKey.GetLTPIdxKey(), &redis.Z{
		Score:  key.GetScore(),
		Member: key.GetLTPKey()}).Result()
	if err != nil {
		log.Println("Failed setting tick LTP IDX to redis: ", err)
	}

	_, err = rdb.ZAdd(ctx, idxKey.GetVOLIdxKey(), &redis.Z{
		Score:  key.GetScore(),
		Member: key.GetVOLKey()}).Result()
	if err != nil {
		log.Println("Failed setting tick VOL IDX to redis: ", err)
	}
}

func WriteHistCandlesToRedis(ctx context.Context, rdb *redis.Client, candles *[]models.Candle, wg *sync.WaitGroup) {
	defer wg.Done()
	c := 0
	tokenId := uint32(0)
	for _, candle := range *candles {
		c++
		tokenId = candle.InstrumentToken
		key := redistypes.NewKey(candle.TS, candle.InstrumentToken)
		idxKey := redistypes.NewIdxKey(candle.InstrumentToken)

		ohlcv := candle.OHLCV
		_, err := rdb.HSet(ctx, key.GetCS15MKey(),
			"O", fmt.Sprintf("%f", ohlcv.Open),
			"H", fmt.Sprintf("%f", ohlcv.High),
			"L", fmt.Sprintf("%f", ohlcv.Low),
			"C", fmt.Sprintf("%f", ohlcv.Close),
			"V", fmt.Sprintf("%d", ohlcv.Volume)).Result()
		if err != nil {
			log.Printf("Failed writting candle: %s to reids. Err: %v", key.GetCS15MKey(), err)
			continue
		}

		_, err = rdb.ZAdd(ctx, idxKey.GetCS15MIdxKey(),
			&redis.Z{
				Score:  key.GetScore(),
				Member: key.GetCS15MKey(),
			}).Result()
		if err != nil {
			log.Printf("Failed writting candle index: %s to reids. Err: %v", key.GetCS15MKey(), err)
			continue
		}
	}
	log.Printf("Set %d candles for %d in redis...", c, tokenId)
}

func WriteCandleToRedis(ctx context.Context, rdb *redis.Client, key redistypes.RedisKey, ohlcv models.OHLCV) {
	panic("not implemented")
}

func GetVolume(ctx context.Context, rdb *redis.Client, key redistypes.RedisKey) (uint32, error) {
	v, err := rdb.Get(ctx, key.GetVOLKey()).Result()
	switch {
	case err == redis.Nil:
		v = "0"
	case err != nil:
		log.Printf("Failed getting VOL value for Key: %v. Err: %v", key.GetVOLKey(), err)
		return 0, err
	case v == "":
		v = "0"
	}
	vol, err := strconv.ParseInt(v, 10, 32)
	if err != nil {
		log.Printf("Failed converting VOL %s to int. Err: %v", v, err)
		return 0, err
	}

	return uint32(vol), nil
}

package marketdata

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"sync"
	"time"

	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/go/models"
	redisTypes "org.hbb/algo-trading/go/pkg/redis/types"
	envutils "org.hbb/algo-trading/go/pkg/utils/env"
)

const (
	RedisHistDb      = iota //keyspace : 0
	RedisRtDb               //keyspace : 1
	RedisDialTimeout = 250
)

func InitRealTimeRedisClient() (context.Context, *redis.Client) {
	return context.Background(), GetRTRedisClient()
}

func GetHistRedisClient() *redis.Client {
	host := envutils.MustGetEnv("REDIS_HIST_HOST")
	port := envutils.MustGetEnv("REDIS_HIST_PORT")
	return getRedisClient(host, port, RedisHistDb)
}

func GetRTRedisClient() *redis.Client {
	host := envutils.MustGetEnv("REDIS_RT_HOST")
	port := envutils.MustGetEnv("REDIS_RT_PORT")
	return getRedisClient(host, port, RedisRtDb)
}

func getRedisClient(host string, port string, redisdb int) *redis.Client {
	redisClient := redis.NewClient(&redis.Options{
		Addr:        fmt.Sprintf("%s:%s", host, port),
		Password:    "",
		DB:          redisdb,
		DialTimeout: RedisDialTimeout * time.Millisecond,
	})

	connected := false
	for i := 0; i <= 10; i++ {
		_, err := redisClient.Ping(context.Background()).Result()
		if err == nil {
			log.Println("Connection to Redis Server established...")
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

	return redisClient
}

func WriteTickToRedis(ctx context.Context, rdb *redis.Client, tick *models.Tick) {
	key := redisTypes.NewKey(tick.ExchangeTS, tick.InstrumentToken)
	idxKey := redisTypes.NewIdxKey(tick.InstrumentToken)
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
		key := redisTypes.NewKey(candle.TS, candle.InstrumentToken)
		idxKey := redisTypes.NewIdxKey(candle.InstrumentToken)

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

func WriteCandleToRedis(ctx context.Context, rdb *redis.Client, key redisTypes.RedisKey, ohlcv models.OHLCV) {
	panic("not implemented")
}

func GetVolume(ctx context.Context, rdb *redis.Client, key redisTypes.RedisKey) (uint32, error) {
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

func PublishMsg(ctx context.Context, rdb *redis.Client, topic string, msg string) {
	_, err := rdb.Publish(ctx, topic, msg).Result()
	if err != nil {
		log.Printf("Failed publishing msg to %s topic. Err: %v", topic, err)
	}
}

func GetOHLCV(ctx context.Context, rdb *redis.Client, key string) (models.OHLCV, error) {
	v, err := rdb.HGetAll(ctx, key).Result()
	if err != nil {
		log.Printf("Failed getting Candlestick value for Key: %v. Err: %v", key, err)
		return models.OHLCV{}, err
	}

	o, err := strconv.ParseFloat(v["O"], 32)
	h, err := strconv.ParseFloat(v["H"], 32)
	l, err := strconv.ParseFloat(v["L"], 32)
	c, err := strconv.ParseFloat(v["C"], 32)
	vol, err := strconv.ParseInt(v["V"], 10, 32)

	ohlcv := models.OHLCV{
		Open:   float32(o),
		High:   float32(h),
		Low:    float32(l),
		Close:  float32(c),
		Volume: uint32(vol),
	}

	return ohlcv, nil
}

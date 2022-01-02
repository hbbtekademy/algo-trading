package main

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"time"

	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/models"
	redistypes "org.hbb/algo-trading/pkg/redis/types"
	"org.hbb/algo-trading/pkg/utils"
	redisutils "org.hbb/algo-trading/pkg/utils/redis"
)

var (
	rdb     *redis.Client
	mktutil *utils.Mktutil
	done    chan bool
)

func main() {
	rdb = redisutils.GetRTRedisClient()
	mktutil = utils.NewMktUtil(utils.GetMarketTime())
	done = make(chan bool)

	now := time.Now()
	log.Println("Now: ", now, 60-now.Second())
	time.Sleep(time.Duration(60-now.Second()+4) * time.Second)

	ticker := time.NewTicker(60 * time.Second)
	go candleTicker(ticker)

	<-done
}

func candleTicker(ticker *time.Ticker) {
	log.Println("Starting candle ticker...")
	ctx := context.Background()
	for {
		t := <-ticker.C

		if mktutil.IsValidMarketHrs(t.Add(-1 * time.Minute)) {
			counter := 0
			ct := t.Add(-15 * time.Second)
			pt := t.Add(-75 * time.Second)
			keyTS := ct.Format(redistypes.REDIS_KEY_TS_FMT)

			keyPat := redistypes.NewKeyPattern(keyTS, "*")
			iter := rdb.Scan(ctx, 0, keyPat.GetLTPKey(), 0).Iterator()
			for iter.Next(ctx) {
				counter++
				key := redistypes.ParseKey(iter.Val())
				go candleGenerator(ctx, key, redistypes.NewKey(pt, key.TokenId))
			}
			if err := iter.Err(); err != nil {
				log.Println("Failed scanning keys: ", err)
			}
			log.Printf("Submitted %d candles for generation for TS: %s", counter, keyTS)
		} else if mktutil.IsAfterMarketHrs(t.Add(-5 * time.Minute)) {
			log.Println("Outside mkt hrs. Exiting...")
			done <- true
		} else if mktutil.IsBeforeMarketHrs(t) {
			log.Println("Waiting for mkt hrs to start....")
		}
	}
}

func candleGenerator(ctx context.Context, cKey redistypes.RedisKey, pKey redistypes.RedisKey) {
	values, err := rdb.LRange(ctx, cKey.GetLTPKey(), 0, -1).Result()
	ohlcv := models.OHLCV{}
	if err != nil {
		log.Printf("Failed getting LTP values for Key: %s. Err: %v", cKey.GetLTPKey(), err)
		return
	}

	for idx, value := range values {
		v, err := strconv.ParseFloat(value, 32)
		ltp := float32(v)
		if err != nil {
			log.Printf("Failed converting LTP %s to float32. Err: %v", value, err)
			return
		}
		if idx == 0 {
			ohlcv.Open = ltp
			ohlcv.High = ltp
			ohlcv.Low = ltp
		}
		if ltp > ohlcv.High {
			ohlcv.High = ltp
		}
		if ltp < ohlcv.Low {
			ohlcv.Low = ltp
		}
		ohlcv.Close = ltp
	}

	value, err := rdb.Get(ctx, cKey.GetVOLKey()).Result()
	if err != nil {
		log.Printf("Failed getting VOL value for Key: %v. Err: %v", cKey.GetVOLKey(), err)
		return
	}
	volEnd, err := strconv.ParseInt(value, 10, 32)
	if err != nil {
		log.Printf("Failed converting VOL %s to int. Err: %v", values[0], err)
		return
	}

	value, err = rdb.Get(ctx, pKey.GetVOLKey()).Result()
	switch {
	case err == redis.Nil:
		value = "0"
	case err != nil:
		log.Printf("Failed getting VOL value for Key: %v. Err: %v", pKey.GetVOLKey(), err)
		return
	case value == "":
		value = "0"
	}
	volStart, err := strconv.ParseInt(value, 10, 32)
	if err != nil {
		log.Printf("Failed converting VOL %s to int. Err: %v", value, err)
		return
	}

	ohlcv.Volume = uint32(volEnd) - uint32(volStart)

	candleKey := cKey.GetCS1MKey()
	idxKey := redistypes.NewIdxKey(cKey.TokenId)

	_, err = rdb.HSet(ctx, candleKey,
		"O", fmt.Sprintf("%f", ohlcv.Open),
		"H", fmt.Sprintf("%f", ohlcv.High),
		"L", fmt.Sprintf("%f", ohlcv.Low),
		"C", fmt.Sprintf("%f", ohlcv.Close),
		"V", fmt.Sprintf("%d", ohlcv.Volume)).Result()
	if err != nil {
		log.Printf("Failed writting candle :%s to reids. Err: %v", candleKey, err)
		return
	}

	_, err = rdb.ZAdd(ctx, idxKey.GetCS1MIdxKey(),
		&redis.Z{
			Score:  cKey.GetScore(),
			Member: candleKey,
		}).Result()
	if err != nil {
		log.Printf("Failed writting candle idx:%s, value:%s to reids. Err: %v",
			idxKey.GetCS1MIdxKey(), candleKey, err)
		return
	}

	log.Printf("Candlestick %s written to redis...", candleKey)
}

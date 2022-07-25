package main

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"sync"
	"time"

	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/go/models"
	redistypes "org.hbb/algo-trading/go/pkg/redis/types"
	"org.hbb/algo-trading/go/pkg/utils"
	redisutils "org.hbb/algo-trading/go/pkg/utils/redis"
)

var (
	rdb     *redis.Client
	mktutil *utils.MarketSpecifications
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
	var wg sync.WaitGroup
	ctx := context.Background()
	tCounter := 0
	for {
		t := <-ticker.C
		tCounter++

		if mktutil.IsValidMarketHrs(t.Add(-1 * time.Minute)) {
			counter := 0
			ct := t.Add(-15 * time.Second)
			pt := t.Add(-75 * time.Second)
			keyTS := ct.Format(redistypes.REDIS_KEY_TS_FMT)

			keyPat := redistypes.NewKeyPattern(keyTS, "*")
			iter := rdb.Scan(ctx, 0, keyPat.GetLTPKey(), 500).Iterator()
			for iter.Next(ctx) {
				counter++
				key := redistypes.ParseKey(iter.Val())
				wg.Add(1)
				go candleGenerator(ctx, key, redistypes.NewKey(pt, key.TokenId), &wg)
			}
			if err := iter.Err(); err != nil {
				log.Println("Failed scanning keys: ", err)
			}

			log.Printf("Submitted %d candles for generation for TS: %s", counter, keyTS)

			wg.Wait()
			log.Println("All 1M candles generated. Sending notification...")

			msg := fmt.Sprintf("CS1M:ts:%s", keyTS)
			redisutils.PublishMsg(ctx, rdb, redistypes.REDIS_CS1M_NOTIFY_TOPIC, msg)
			if tCounter%15 == 0 {
				msg := fmt.Sprintf("CS15M:ts:%s", keyTS)
				log.Println("Sending notification for 15M Candles...")
				redisutils.PublishMsg(ctx, rdb, redistypes.REDIS_CS15M_NOTIFY_TOPIC, msg)
			}

		} else if mktutil.IsAfterMarketHrs(t.Add(-5 * time.Minute)) {
			log.Println("Outside mkt hrs. Exiting...")
			done <- true
		} else if mktutil.IsBeforeMarketHrs(t) {
			log.Println("Waiting for mkt hrs to start....")
		}
	}
}

func candleGenerator(ctx context.Context, cKey redistypes.RedisKey, pKey redistypes.RedisKey, wg *sync.WaitGroup) {
	defer wg.Done()
	values, err := rdb.LRange(ctx, cKey.GetLTPKey(), 0, -1).Result()
	if err != nil {
		log.Printf("Failed getting LTP values for Key: %s. Err: %v", cKey.GetLTPKey(), err)
		return
	}

	ohlcv := models.OHLCV{}
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

	volEnd, err := redisutils.GetVolume(ctx, rdb, cKey)
	if err != nil {
		log.Printf("Failed getting VOL for key:%s. Err: %v", cKey.GetVOLKey(), err)
		return
	}

	volStart, err := redisutils.GetVolume(ctx, rdb, pKey)
	if err != nil {
		log.Printf("Failed getting VOL for key:%s. Err: %v", pKey.GetVOLKey(), err)
		return
	}

	ohlcv.Volume = volEnd - volStart

	candleKey := cKey.GetCS1MKey()
	idxKey := redistypes.NewIdxKey(cKey.TokenId)

	_, err = rdb.HSet(ctx, candleKey,
		"O", fmt.Sprintf("%f", ohlcv.Open),
		"H", fmt.Sprintf("%f", ohlcv.High),
		"L", fmt.Sprintf("%f", ohlcv.Low),
		"C", fmt.Sprintf("%f", ohlcv.Close),
		"V", fmt.Sprintf("%d", ohlcv.Volume)).Result()
	if err != nil {
		log.Printf("Failed writing candle :%s to redis. Err: %v", candleKey, err)
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

package main

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"strings"
	"time"

	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/models"
	"org.hbb/algo-trading/pkg/utils"
)

var (
	rdb     *redis.Client
	mktutil *utils.Mktutil
	done    chan bool
)

func main() {
	rdb = utils.GetRedisClient()
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
			keyTS := ct.Format("200601021504")
			prevKeyTS := pt.Format("200601021504")

			ltpKeyPat := fmt.Sprintf("LTP:ts:sym:%s:*", keyTS)
			iter := rdb.Scan(ctx, 0, ltpKeyPat, 0).Iterator()
			for iter.Next(ctx) {
				counter++
				sym := strings.Split(iter.Val(), ":")[4]
				go candleGenerator(ctx, sym, keyTS, prevKeyTS)
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

func candleGenerator(ctx context.Context, sym string, cts string, pts string) {
	ltpKey := fmt.Sprintf("LTP:ts:sym:%s:%s", cts, sym)
	values, err := rdb.LRange(ctx, ltpKey, 0, -1).Result()
	ohlcv := models.OHLCV{}
	if err != nil {
		log.Printf("Failed getting LTP values for Key: %v. Err: %v", ltpKey, err)
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

	volKey := fmt.Sprintf("VOL:ts:sym:%s:%s", cts, sym)
	value, err := rdb.Get(ctx, volKey).Result()
	if err != nil {
		log.Printf("Failed getting VOL value for Key: %v. Err: %v", volKey, err)
		return
	}
	volEnd, err := strconv.ParseInt(value, 10, 32)
	if err != nil {
		log.Printf("Failed converting VOL %s to int. Err: %v", values[0], err)
		return
	}

	pVolKey := fmt.Sprintf("VOL:ts:sym:%s:%s", pts, sym)
	value, err = rdb.Get(ctx, pVolKey).Result()
	switch {
	case err == redis.Nil:
		value = "0"
	case err != nil:
		log.Printf("Failed getting VOL value for Key: %v. Err: %v", pVolKey, err)
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

	candleKey := fmt.Sprintf("CS1M:ts:sym:%s:%s", cts, sym)

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
	log.Printf("Candlestick %s written to redis...", candleKey)
}

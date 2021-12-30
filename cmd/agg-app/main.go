package main

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"strings"
	"time"

	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/pkg/utils"
)

type Tick struct {
	Sym    string
	ExchTS time.Time
	LTP    float32
	Vol    int64
}

type OHLCV struct {
	Open   float32
	High   float32
	Low    float32
	Close  float32
	Volume int64
}

type Candle struct {
	TS    time.Time
	Sym   string
	OHLCV *OHLCV
}

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
		if mktutil.IsValidMarketHrs(t) {
			counter := 0
			t = t.Add(-15 * time.Second)
			keyTS := t.Format("200601021504")
			ltpKeyPat := fmt.Sprintf("LTP:ts:sym:%s:*", keyTS)

			keys, err := rdb.Keys(ctx, ltpKeyPat).Result()
			if err != nil {
				log.Fatalln("failed getting keys from redis: ", err)
			}

			for _, key := range keys {
				counter++
				sym := strings.Split(key, ":")[4]
				go candleGenerator(ctx, sym, keyTS)
			}
			log.Printf("Submitted %d candles for generation for TS: %s", counter, keyTS)
		} else if mktutil.IsAfterMarketHrs(t.Add(5 * time.Minute)) {
			log.Println("Outside mkt hrs. Exiting...")
			done <- true
		} else if mktutil.IsBeforeMarketHrs(t) {
			log.Println("Waiting for mkt hrs to start....")
		}
	}
}

func candleGenerator(ctx context.Context, sym string, ts string) {
	ltpKey := fmt.Sprintf("LTP:ts:sym:%s:%s", ts, sym)
	values, err := rdb.LRange(ctx, ltpKey, 0, -1).Result()
	ohlcv := OHLCV{}
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

	volKey := fmt.Sprintf("VOL:ts:sym:%s:%s", ts, sym)
	values, err = rdb.LRange(ctx, volKey, 0, -1).Result()
	if err != nil {
		log.Printf("Failed getting VOL value for Key: %v. Err: %v", volKey, err)
		return
	}

	volStart, err := strconv.ParseInt(values[0], 10, 32)
	if err != nil {
		log.Printf("Failed converting VOL %s to int. Err: %v", values[0], err)
		return
	}
	volEnd, err := strconv.ParseInt(values[len(values)-1], 10, 32)
	if err != nil {
		log.Printf("Failed converting VOL %s to int. Err: %v", values[len(values)-1], err)
		return
	}
	ohlcv.Volume = volEnd - volStart

	candleKey := fmt.Sprintf("CS1M:ts:sym:%s:%s", ts, sym)

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

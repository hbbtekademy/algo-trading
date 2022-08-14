package main

import (
	"context"
	"flag"
	"log"
	"sync"
	"time"

	"github.com/go-redis/redis/v8"
	kiteConnect "github.com/zerodha/gokiteconnect/v4"
	"org.hbb/algo-trading/go/models"
	instmanager "org.hbb/algo-trading/go/pkg/repository/instruments"
	redisUtils "org.hbb/algo-trading/go/pkg/repository/marketdata"
	apiUtils "org.hbb/algo-trading/go/pkg/utils/api"
)

type CmdArgs struct {
	Interval string
	From     time.Time
	To       time.Time
}

var (
	kc  *kiteConnect.Client
	rdb *redis.Client
)

// Back-fill is to get Historical Data / On-boarding new instruments
func main() {
	start := time.Now()
	var wg sync.WaitGroup
	ctx := context.Background()
	cmdArgs := parseCmdLineArgs()
	kc = apiUtils.GetKiteClient()
	rdb = redisUtils.GetHistRedisClient()
	instruments := instmanager.GetAllInstruments()

	for tokenId, instrument := range instruments {
		log.Printf("Token: %d, Instrument: %v", tokenId, instrument)
		candles := getHistCandles(tokenId, cmdArgs.Interval, cmdArgs.From, cmdArgs.To)
		wg.Add(1)
		go redisUtils.WriteHistCandlesToRedis(ctx, rdb, candles, &wg)
	}

	log.Printf("Waiting for all goroutines to finish...")
	wg.Wait()
	end := time.Now()
	log.Printf("Done writing all hist data to redis in %f seconds. Exiting...", end.Sub(start).Seconds())
}

func getBFInstruments() models.Instruments {
	instruments := instmanager.GetNifty100()
	mid := instmanager.GetNiftyMid50()
	for k, v := range mid {
		instruments[k] = v
	}
	small := instmanager.GetNiftySmall50()
	for k, v := range small {
		instruments[k] = v
	}
	indices := instmanager.GetIndices()
	for k, v := range indices {
		instruments[k] = v
	}
	startup := instmanager.GetNiftyStartup()
	for k, v := range startup {
		instruments[k] = v
	}
	return instruments
}

func getHistCandles(tokenId uint32, interval string, from time.Time, to time.Time) *[]models.Candle {
	var candles []models.Candle
	now := time.Now()
	fromTime := from
	toTime := from.AddDate(0, 0, 120)
	for {
		if toTime.After(now.AddDate(0, 0, 120)) {
			log.Println("Got required duration data. Exiting loop")
			break
		}

		histData, err := kc.GetHistoricalData(int(tokenId), interval, fromTime, toTime, false, false)
		if err != nil {
			log.Printf("Error getting historical data for range %s to %s. Error:%v Retrying...", fromTime, toTime, err)
			continue
		}

		for _, hist := range histData {
			candles = append(candles, models.Candle{
				TS:              hist.Date.Time,
				InstrumentToken: tokenId,
				Sym:             "",
				OHLCV: &models.OHLCV{
					Open:   float32(hist.Open),
					High:   float32(hist.High),
					Low:    float32(hist.Low),
					Close:  float32(hist.Close),
					Volume: uint32(hist.Volume),
				},
			})
		}

		fromTime = toTime
		toTime = fromTime.AddDate(0, 0, 60)
	}

	return &candles
}

func parseCmdLineArgs() *CmdArgs {
	cmdInterval := flag.String("interval", "15minute", "Candle interval - minute, 15minute, 30minute etc")
	cmdFrom := flag.String("from", "2015-01-01 00:00:00", "From backfill time in YYYY-MM-DD HH:MM:SS format")
	cmdTo := flag.String("to", "2021-12-31 23:59:59", "To backfill time in YYYY-MM-DD HH:MM:SS format")
	flag.Parse()

	if *cmdInterval == "" {
		log.Fatalf("Candle interval (-interval) not provided.")
	}
	if *cmdFrom == "" {
		log.Fatalf("From backfill time not provided.")
	}
	if *cmdTo == "" {
		log.Fatalf("To backfill not provided.")
	}

	fromTime, err := time.Parse("2006-01-02 15:04:05", *cmdFrom)
	if err != nil {
		log.Fatalf("From backfill time format incorrect. Enter time in YYYY-MM-DD HH:MM:SS format. Err:%v", err)
	}
	toTime, err := time.Parse("2006-01-02 15:04:05", *cmdTo)
	if err != nil {
		log.Fatalf("To backfill time format incorrect. Enter time in YYYY-MM-DD HH:MM:SS format. Err:%v", err)
	}

	cmdArgs := &CmdArgs{
		Interval: *cmdInterval,
		From:     fromTime,
		To:       toTime,
	}

	return cmdArgs
}

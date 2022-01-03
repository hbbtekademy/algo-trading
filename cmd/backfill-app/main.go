package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"time"

	"github.com/go-redis/redis/v8"
	kiteconnect "github.com/zerodha/gokiteconnect/v4"
	"org.hbb/algo-trading/models"
	instmanager "org.hbb/algo-trading/pkg/instrument-manager"
	redistypes "org.hbb/algo-trading/pkg/redis/types"
	"org.hbb/algo-trading/pkg/utils"
	redisutils "org.hbb/algo-trading/pkg/utils/redis"
)

type CmdArgs struct {
	Interval string
	From     time.Time
	To       time.Time
}

var (
	kc  *kiteconnect.Client
	rdb *redis.Client
)

func main() {
	ctx := context.Background()
	cmdArgs := parseCmdLineArgs()
	kc = utils.GetKiteClient()
	rdb = redisutils.GetHistRedisClient()
	instruments := instmanager.GetAllInstruments()

	for tokenId, instrument := range instruments {
		log.Printf("Token: %d, Instrument: %v", tokenId, instrument)
		candles := getHistCandles(tokenId, cmdArgs.Interval, cmdArgs.From, cmdArgs.To)
		c := 0
		for _, candle := range *candles {
			c++
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

package smash

import (
	"context"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	"github.com/go-redis/redis/v8"
	"org.hbb/algo-trading/go/models"
	"org.hbb/algo-trading/go/pkg/repository/marketdata"
	redisUtils "org.hbb/algo-trading/go/pkg/repository/marketdata"
)

var (
	redisClient *redis.Client
	ctx         context.Context
)

func Start() {
	/**
	1. At 9 AM - Create File for the Day.
	2. At 915 AM - Start reading 1 record from the file per second
	3. After 1 record is read, write the record to Redis Real Time DB
	*/

	//ctx, redisClient = redisUtils.InitRealTimeRedisClient()
	ctx, redisClient = redisUtils.InitHistoricalRedisClient()

	records := readCsvFile("./SMASH-MOCK-tickdata.csv")
	fmt.Println("No of records", len(records))

	for _, element := range records {
		cbTick := mapRecordToCBTick(element)
		marketdata.WriteTickToRedis(ctx, redisClient, cbTick)
		//sleep 1 second
	}
}

func mapRecordToCBTick(element []string) *models.Tick {
	cbTick := &models.Tick{
		InstrumentToken:    9999,
		Sym:                "SMASH",
		ExchangeTS:         getTs(element[0]),
		LastTradeTS:        getTs(element[0]),
		LTP:                getFloat(element[4]),
		LastTradedQuantity: getInt(element[4]),
		VolumeTraded:       getInt(element[5]),
	}
	return cbTick
}

func getFloat(message string) float32 {
	lastTradedPrice, _ := strconv.ParseFloat(message, 32)
	return float32(lastTradedPrice)
}

func getInt(message string) uint32 {
	lastTradedPrice, _ := strconv.ParseInt(message, 10, 32)
	return uint32(lastTradedPrice)
}

func getTs(message string) time.Time {
	angelOneTimeFormat := "02/01/2006 15:04:05"
	indiaTimeZoneFormat := "Asia/Kolkata"
	indiaLocation, _ := time.LoadLocation(indiaTimeZoneFormat)

	ts, _ := time.ParseInLocation(angelOneTimeFormat, message, indiaLocation)
	return ts
}

func readCsvFile(filePath string) [][]string {
	f, err := os.Open(filePath)
	if err != nil {
		log.Fatal("Unable to read input file "+filePath, err)
	}
	defer f.Close()

	csvReader := csv.NewReader(f)
	records, err := csvReader.ReadAll()
	if err != nil {
		log.Fatal("Unable to parse file as CSV for "+filePath, err)
	}

	return records
}

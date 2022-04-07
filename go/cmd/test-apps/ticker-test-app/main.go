package main

import (
	"bufio"
	"context"
	"flag"
	"log"
	"os"
	"strconv"
	"strings"
	"time"

	"org.hbb/algo-trading/go/models"
	instmanager "org.hbb/algo-trading/go/pkg/instrument-manager"
	redisutils "org.hbb/algo-trading/go/pkg/utils/redis"
)

type Instruments map[string]uint32

var (
	instruments Instruments
	now         time.Time
	first       bool
	diff        time.Duration
)

func main() {
	start := time.Now()
	instruments = getInstruments()
	now = time.Now()
	first = true
	ctx := context.Background()
	rdb := redisutils.GetRTRedisClient()

	tfCmdArg := flag.String("tf", "", "Full Ticker File Path")
	flag.Parse()

	if *tfCmdArg == "" {
		log.Fatalln("Please provide input file")
	}

	f, err := os.Open(*tfCmdArg)
	if err != nil {
		log.Fatalf("Unable to open file %s. Err: %v", *tfCmdArg, err)
	}
	defer f.Close()

	sc := bufio.NewScanner(f)
	l := 0
	for sc.Scan() {
		l++
		tick := getTick(sc.Text())
		//log.Println(tick)
		redisutils.WriteTickToRedis(ctx, rdb, tick)
		if l%50000 == 0 {
			log.Printf("Processed %d lines", l)
		}
	}

	end := time.Now()
	log.Printf("Done publishing %d ticks to redis in %f seconds", l, end.Sub(start).Seconds())
}

func getInstruments() Instruments {
	i := instmanager.GetAllInstruments()
	instruments := make(Instruments)
	for k, v := range i {
		instruments[v.Sym] = k
	}

	return instruments
}

func getTick(s string) *models.Tick {
	arr := strings.Split(s, ",")
	sym := arr[0]
	exchTS, _ := time.Parse(time.RFC3339, arr[1])
	lastTradeTS, _ := time.Parse(time.RFC3339, arr[2])
	ltp, _ := strconv.ParseFloat(arr[3], 32)
	lastTradedQuantity, _ := strconv.ParseInt(arr[4], 10, 32)
	vol, _ := strconv.ParseInt(arr[5], 10, 32)

	// Calculate the modified ExchTS offset from current time
	if first {
		diff = now.Sub(exchTS) + 3*time.Minute
		first = false
	}

	modExchTS := exchTS.Add(diff)

	return &models.Tick{
		Sym:                sym,
		InstrumentToken:    instruments[sym],
		ExchTS:             modExchTS,
		LastTradeTS:        lastTradeTS,
		LTP:                float32(ltp),
		LastTradedQuantity: uint32(lastTradedQuantity),
		VolumeTraded:       uint32(vol),
	}
}

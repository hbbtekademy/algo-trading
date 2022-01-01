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

	"org.hbb/algo-trading/models"
	instmanager "org.hbb/algo-trading/pkg/instrument-manager"
	"org.hbb/algo-trading/pkg/utils"
)

type Instruments map[string]uint32

var (
	instruments Instruments
	now         time.Time
	first       bool
	diff        time.Duration
)

func main() {

	instruments = getInstruments()
	now = time.Now()
	first = true
	ctx := context.Background()
	rdb := utils.GetRedisClient(utils.MustGetEnv("REDIS_HOST"), utils.MustGetEnv("REDIS_PORT"))

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
	for sc.Scan() {
		tick := getTick(sc.Text())
		log.Println(tick)
		utils.WriteTickToRedis(ctx, rdb, tick)
	}

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
		diff = now.Sub(exchTS)
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

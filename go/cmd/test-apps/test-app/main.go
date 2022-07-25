package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	instmanager "org.hbb/algo-trading/go/pkg/instrument-manager"
	redistypes "org.hbb/algo-trading/go/pkg/redis/types"
)

var ctx = context.Background()

func main() {

	instruments := instmanager.GetNFOFut()
	for _, inst := range instruments {
		if !strings.Contains(inst.Sym, "22FEB") {
			continue
		}
		sym := strings.Split(inst.Sym, "22")[0]
		//sym := inst.Sym
		lot := inst.LotSize
		cmd := fmt.Sprintf("python python/strategy/rsi_sell.py \"/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/BackTest/NSEHist15min/%s-HIST-15M.csv\" \"%s\" %d >> results_Cash_Sell_2021.csv",
			sym, sym, lot)
		cmd = fmt.Sprintf("%s,%d,2022-01-26,2022-02-02,2022-02-01", inst.Sym, lot)
		fmt.Println(cmd)
	}
	os.Exit(0)

	//test code ?
	now := time.Now()
	ts, _ := time.Parse(time.RFC3339, "2022-01-02T20:27:17+05:30")
	key := redistypes.NewKey(ts, 1234)
	log.Printf("Now: %s, TS: %s, LTPKey: %s, Token: %d, Score: %f %f",
		now.Format(time.RFC3339),
		key.TS.Format(time.RFC3339),
		key.GetLTPKey(),
		key.TokenId,
		key.GetScore(),
		float64(key.TS.Unix()))
	ts, _ = time.Parse(time.RFC3339, "2022-01-02T20:28:00+05:30")
	key = redistypes.NewKey(ts, 1234)
	log.Printf("Now: %s, TS: %s, LTPKey: %s, Token: %d, Score: %f %f",
		now.Format(time.RFC3339),
		key.TS.Format(time.RFC3339),
		key.GetLTPKey(),
		key.TokenId,
		key.GetScore(),
		float64(key.TS.Unix()))

	/*
		fmt.Printf("Num: %02d", 9)

		rdb := redis.NewClient(&redis.Options{
			Addr:        "34.93.71.75:6379",
			Password:    "",
			DB:          0,
			DialTimeout: 1 * time.Second,
		})

		v, e := rdb.Get(ctx, "abc").Result()
		if e == redis.Nil {
			v = "0"
		}
		log.Printf("Value: %v, err:%v", v, e)

		err := rdb.Set(ctx, "key", "value", 0).Err()
		if err != nil {
			log.Fatalln("Failed setting value in redis", err)
		}
		count := 0
		start := time.Now()
		keys := rdb.Keys(ctx, "1LTP:ts:sym*")
		for _, key := range keys.Val() {
			log.Println("Getting LTP for key:", key)
			prices := rdb.LRange(ctx, key, 0, -1)
			for _, v := range prices.Val() {
				count++
				ltp, _ := strconv.ParseFloat(v, 32)
				log.Println("LTP:", float32(ltp))
			}
			break
		}
		end := time.Now()
		log.Printf("No of records processed: %d, Time taken: %f", count, end.Sub(start).Seconds())
	*/

	/*
		f, err := os.OpenFile("/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/Ticker-20211227.csv", os.O_RDONLY, os.ModePerm)
		if err != nil {
			log.Fatalf("Failed reading file: %v", err)
		}
		defer f.Close()

		sc := bufio.NewScanner(f)
		for sc.Scan() {
			line := sc.Text()
			if strings.HasPrefix(line, "RELIANCE,") {
				arr := strings.Split(line, ",")
				ts, _ := time.Parse(time.RFC3339, arr[1])
				s := fmt.Sprintf("rpush LTP:ts:sym:%s:RELIANCE %s", ts.Format("200601021504"), arr[3])
				fmt.Println(s)
			}
		}*/
}

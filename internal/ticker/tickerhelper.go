package ticker

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	kitemodels "github.com/zerodha/gokiteconnect/v4/models"
)

func createTickFile() {
	var err error
	y, m, d := time.Now().Date()
	fn := fmt.Sprintf("Ticker-%d%d%d.csv", y, int(m), d)

	tickFile, err = os.OpenFile(fn, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalln("Error opening ticker file:", err)
	}

	log.Printf("Tick file %s created...", fn)
}

func writeToCsv(tick kitemodels.Tick) {
	w := csv.NewWriter(tickFile)
	defer w.Flush()

	err := w.Write(getTickData(tick))
	if err != nil {
		log.Fatalln("Error writing to ticker file:", err)
	}
}

func getTickData(tick kitemodels.Tick) []string {
	return []string{strconv.Itoa(int(tick.InstrumentToken)),
		tick.Timestamp.Format(time.RFC3339),
		tick.LastTradeTime.Format(time.RFC3339),
		fmt.Sprintf("%f", tick.LastPrice),
		fmt.Sprintf("%d", tick.LastTradedQuantity),
		fmt.Sprintf("%d", tick.VolumeTraded),
	}
}

func getMarketTime() (time.Time, time.Time) {
	y, m, d := time.Now().Date()
	st, err := time.Parse(time.RFC3339, fmt.Sprintf("%d-%d-%dT08:59:59+05:30", y, int(m), d))
	if err != nil {
		log.Fatalln("failed getting market start time:", err)
	}

	et, err := time.Parse(time.RFC3339, fmt.Sprintf("%d-%d-%dT16:01:00+05:30", y, int(m), d))
	if err != nil {
		log.Fatalln("failed getting market end time:", err)
	}

	return st, et
}

func getInstruments() []uint32 {
	return []uint32{
		5633,
		6401,
		912129,
		3861249,
		2616577,
		325121,
		40193,
		60417,
		70401,
		5097729,
		1510401,
		4267265,
		81153,
		4268801,
		78081,
		579329,
		1195009,
		103425,
		134657,
		2714625,
		2911489,
		558337,
		140033,
		2029825,
		175361,
		177665,
		5215745,
		3876097,
		197633,
		2800641,
		3771393,
		225537,
		232961,
		1207553,
		303617,
		2585345,
		315393,
		2513665,
		1850625,
		340481,
		1086465,
		341249,
		119553,
		345089,
		348929,
		359937,
		356865,
		1270529,
		5573121,
		4774913,
		415745,
		2883073,
		7458561,
		1346049,
		3520257,
		408065,
		2865921,
		424961,
		1723649,
		3001089,
		4632577,
		492033,
		4561409,
		2939649,
		2672641,
		519937,
		1041153,
		2815745,
		6054401,
		4598529,
		3924993,
		2977281,
		633601,
		6191105,
		681985,
		617473,
		3834113,
		240641,
		2730497,
		738561,
		4600577,
		5582849,
		794369,
		806401,
		779521,
		758529,
		857857,
		2953217,
		878593,
		884737,
		895745,
		3465729,
		897537,
		900609,
		2952193,
		2674433,
		2889473,
		784129,
		969473,
		3050241,
	}
}

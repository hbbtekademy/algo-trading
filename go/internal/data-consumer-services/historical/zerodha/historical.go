package zerodha

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"time"

	kiteconnect "github.com/zerodha/gokiteconnect/v4"
	"org.hbb/algo-trading/go/models"
	instrumentmanager "org.hbb/algo-trading/go/pkg/repository/instruments"
	secretmanager "org.hbb/algo-trading/go/pkg/secret-manager"
)

var (
	kc *kiteconnect.Client
)

func Start() {
	perfStartTime := time.Now()
	apiKey := secretmanager.GetSecret(secretmanager.KiteApiKeySK)
	accessToken := secretmanager.GetSecret(secretmanager.KiteAccessTokenSK)

	kc = kiteconnect.New(apiKey)
	kc.SetAccessToken(accessToken)

	instruments := instrumentmanager.GetNiftyFutInstruments()
	for _, inst := range instruments {
		log.Printf("Getting historical data for %s", inst.Sym)
		processHistData(inst)
		time.Sleep(2 * time.Second)
	}

	perfEndTime := time.Now()
	log.Printf("Done getting historical data for all symbols in %f minutes...", perfEndTime.Sub(perfStartTime).Minutes())
}

func processHistData(instrument *models.Instrument) {
	histFile := openHistFile(instrument)
	getKiteHistData(instrument.Id, "15minute", histFile)
	closeHistFile(histFile)
}

func getKiteHistData(id uint32, interval string, file *os.File) {
	w := csv.NewWriter(file)
	defer w.Flush()

	err := w.Write(getHistHeader())
	if err != nil {
		log.Fatalln("Error writing header to hist file:", err)
	}

	now := time.Now()
	//fromTime, _ := time.Parse("2006-01-02 15:04:05", "2015-01-01 00:00:00")
	fromTime, _ := time.Parse("2006-01-02 15:04:05", "2022-01-01 00:00:00")
	for {
		toTime := fromTime.AddDate(0, 0, 120)

		if toTime.After(now.AddDate(0, 0, 120)) {
			log.Println("Got required duration data. Exiting loop")
			break
		}

		histData, err := kc.GetHistoricalData(int(id), interval, fromTime, toTime, false, false)
		if err != nil {
			log.Println("Failed to get Hist data: ", err)
			break
		}

		log.Printf("Getting batch From:%s, To:%s, records:%d", fromTime, toTime, len(histData))

		for _, data := range histData {
			//log.Printf("Date: %v, O: %f, H: %f, L: %f, C: %f, V: %d", data.Date, data.Open, data.High, data.Low, data.Close, data.Volume)
			err := w.Write(getHistData(data))
			if err != nil {
				log.Fatalln("Error writing to hist file:", err)
			}
		}
		fromTime = toTime
	}
}

func closeHistFile(histFile *os.File) {
	if histFile != nil {
		histFile.Close()
	}
}

func openHistFile(instrument *models.Instrument) *os.File {
	fn := fmt.Sprintf("./python/BackTest/Hist15min/%s-HIST-15M.csv", instrument.Sym)

	histFile, err := os.OpenFile(fn, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalln("Error creating hist file:", err)
	}

	log.Printf("Hist File %s opened...", fn)

	return histFile
}

func getHistHeader() []string {
	return []string{"Date", "Open", "High", "Low", "Close", "Volume"}
}

func getHistData(data kiteconnect.HistoricalData) []string {
	return []string{
		data.Date.Format(time.RFC3339),
		fmt.Sprintf("%f", data.Open),
		fmt.Sprintf("%f", data.High),
		fmt.Sprintf("%f", data.Low),
		fmt.Sprintf("%f", data.Close),
		fmt.Sprintf("%d", data.Volume),
	}
}

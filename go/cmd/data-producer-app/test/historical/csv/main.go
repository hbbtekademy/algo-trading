package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"
)

const (
	indiaTimeZoneFormat = "Asia/Kolkata"
)

var (
	indiaLocation *time.Location
)

func init() {
	indiaLocation, _ = time.LoadLocation(indiaTimeZoneFormat)
}

func main() {
	/**
	1. Create a CSV file
	2. Increment timestamp by 1 second. Start time 9:15 AM, End time 3:30 PM
	3. Populate CBTick
	4. Write to the CSV file
	*/
	log.Printf("Start File creation")
	fileName := fmt.Sprintf("./%s-tickdata.csv", "SMASH-MOCK")

	tickDataFile, err := os.OpenFile(fileName, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalln("Error creating mock tick data file:", err)
	}

	startTime := time.Date(2022, time.August, 10, 9, 15, 0, 0, indiaLocation)
	endTime := time.Date(2022, time.August, 10, 15, 30, 0, 0, indiaLocation)

	w := csv.NewWriter(tickDataFile)
	defer w.Flush()

	fileWriteError := w.Write(getHistHeader())
	if fileWriteError != nil {
		log.Fatalln("Error writing header to tick data file:", err)
	}

	open := 100
	high := 150
	low := 50
	close := 125
	volume := 1000

	createData(startTime, endTime, w, open, high, low, close, volume, err, time.Second)
	log.Printf(" File creation completed.")
}

func createData(startTime time.Time, endTime time.Time, w *csv.Writer, open int,
	high int, low int, close int, volume int, err error, d time.Duration) {
	for ok := true; ok; ok = startTime.Before(endTime) {

		startTime = startTime.Add(d)
		writeError := w.Write([]string{startTime.Format("02/01/2006 15:04:05"), strconv.Itoa(open),
			strconv.Itoa(high), strconv.Itoa(low), strconv.Itoa(close), strconv.Itoa(volume)})

		close = close + 100
		volume = volume + 1000

		if writeError != nil {
			log.Fatalln("Error writing record to tick data file:", err)
		}
	}
}

func getHistHeader() []string {
	return []string{"Date", "Open", "High", "Low", "Close", "Volume"}
}

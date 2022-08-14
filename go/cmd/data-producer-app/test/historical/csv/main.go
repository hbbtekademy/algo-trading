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

	startTime := time.Date(2022, time.August, 11, 9, 15, 0, 0, indiaLocation)
	endTime := time.Date(2022, time.August, 11, 15, 30, 0, 0, indiaLocation)

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

	for ok := true; ok; ok = startTime.Before(endTime) {
		startTime = startTime.Add(time.Second)
		writeError := w.Write([]string{startTime.Format("02/01/2006 15:04:05"), strconv.Itoa(open),
			strconv.Itoa(high), strconv.Itoa(low), strconv.Itoa(close), strconv.Itoa(volume)})

		close = close + 100
		volume = volume + 1000

		if writeError != nil {
			log.Fatalln("Error writing record to tick data file:", err)
		}
	}
	log.Printf(" File creation completed.")
}

func getHistHeader() []string {
	return []string{"Date", "Open", "High", "Low", "Close", "Volume"}
}

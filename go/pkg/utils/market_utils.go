package utils

import (
	"fmt"
	"log"
	"time"
)

const (
	timeFormatPatternPrefix                string = "%d-%02d-%02dT"
	indiaMarketStartTime                   string = "08:59:59+05:30"
	indiaMarketEndTime                     string = "16:00:00+05:30"
	marketStartTimeCalcFailureErrorMessage string = "Failed to get market start time:"
	marketEndTimeCalcFailureErrorMessage   string = "Failed to get market end time:"
)

/*
MarketSpecifications - This struct will capture all attributes specific to the market
marketStartTime - Local time when the market opens
marketEndTime - Local time when the market closes
marketStartTimeUTC - UTC time when the market opens
marketEndTimeUTC - UTC time when the market closes
marketName - NSE,BSE,NYSE,NASDAQ,CME,Binance,FX
isMarket247 -set to true when the market is always open
*/
type MarketSpecifications struct {
	marketStartTime time.Time
	marketEndTime   time.Time
}

// NewMktUtil /* TODO: Refactor - MarketUtils must know the start and end time of the market.
func NewMktUtil(mst time.Time, met time.Time) *MarketSpecifications {
	return &MarketSpecifications{
		marketStartTime: mst,
		marketEndTime:   met,
	}
}

func (m *MarketSpecifications) IsMarketOpen(t time.Time) bool {
	return t.After(m.marketStartTime) && t.Before(m.marketEndTime)
}

func (m *MarketSpecifications) IsAfterMarketHrs(t time.Time) bool {
	return t.After(m.marketEndTime)
}

func (m *MarketSpecifications) IsBeforeMarketHrs(t time.Time) bool {
	return t.Before(m.marketStartTime)
}

func GetMarketTime() (time.Time, time.Time) {
	y, m, d := time.Now().Date()
	marketStartTime := getMarketTime(y, m, d, timeFormatPatternPrefix+indiaMarketStartTime, marketStartTimeCalcFailureErrorMessage)
	marketEndTime := getMarketTime(y, m, d, timeFormatPatternPrefix+indiaMarketEndTime, marketEndTimeCalcFailureErrorMessage)

	return marketStartTime, marketEndTime
}

func getMarketTime(y int, m time.Month, d int, timeAsString string, logMessage string) time.Time {
	marketTime, err := GetTime(y, m, d, timeAsString)
	if err != nil {
		log.Fatalln(logMessage, err)
	}
	return marketTime
}

func GetTime(y int, m time.Month, d int, timeAsString string) (time.Time, error) {
	return time.Parse(time.RFC3339, fmt.Sprintf(timeAsString, y, int(m), d))
}

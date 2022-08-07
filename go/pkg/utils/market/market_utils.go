package market

import (
	"fmt"
	"log"
	"time"

	"org.hbb/algo-trading/go/models"
)

const (
	timeFormatPatternPrefix                string = "%d-%02d-%02dT"
	indiaMarketStartTime                   string = "08:59:59+05:30"
	indiaMarketEndTime                     string = "16:00:00+05:30"
	marketStartTimeCalcFailureErrorMessage string = "Failed to get market start time:"
	marketEndTimeCalcFailureErrorMessage   string = "Failed to get market end time:"
)

func getMarketSpecs(mst time.Time, met time.Time) *models.MarketSpecifications {
	return &models.MarketSpecifications{
		MarketStartTime: mst,
		MarketEndTime:   met,
	}
}

func InitMarketSpecification() *models.MarketSpecifications {
	marketStartTime, marketEndTime := GetMarketTime()
	marketSpecifications := getMarketSpecs(marketStartTime, marketEndTime)
	log.Printf("Mkt Start Time: %v, Mkt End time: %v", marketStartTime, marketEndTime)
	return marketSpecifications
}

func GetMarketTime() (time.Time, time.Time) {
	y, m, d := time.Now().Date()
	marketStartTime := getMarketTime(y, m, d,
		timeFormatPatternPrefix+indiaMarketStartTime, marketStartTimeCalcFailureErrorMessage)
	marketEndTime := getMarketTime(y, m, d,
		timeFormatPatternPrefix+indiaMarketEndTime, marketEndTimeCalcFailureErrorMessage)

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

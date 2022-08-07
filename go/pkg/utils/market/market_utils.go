package market

import (
	"log"
	"time"

	"org.hbb/algo-trading/go/models"
	timeUtils "org.hbb/algo-trading/go/pkg/utils/time"
)

const (
	timeFormatPatternPrefix                string = "%d-%02d-%02dT"
	indiaMarketStartTime                   string = "08:59:59+05:30"
	indiaMarketEndTime                     string = "16:00:00+05:30"
	marketStartTimeCalcFailureErrorMessage string = "Failed to get market start time:"
	marketEndTimeCalcFailureErrorMessage   string = "Failed to get market end time:"
)

func InitMarketSpecification() *models.MarketSpecifications {
	marketStartTime, marketEndTime := getMarketTime()
	marketSpecifications := getMarketSpecs(marketStartTime, marketEndTime)
	log.Printf("Mkt Start Time: %v, Mkt End time: %v", marketStartTime, marketEndTime)
	return marketSpecifications
}

func getMarketSpecs(marketStartTime time.Time, marketEndTime time.Time) *models.MarketSpecifications {
	return &models.MarketSpecifications{
		MarketStartTime: marketStartTime,
		MarketEndTime:   marketEndTime,
	}
}

func getMarketTime() (time.Time, time.Time) {
	y, m, d := time.Now().Date()
	marketStartTime := timeUtils.GetTime(y, m, d,
		timeFormatPatternPrefix+indiaMarketStartTime, time.RFC3339, marketStartTimeCalcFailureErrorMessage)
	marketEndTime := timeUtils.GetTime(y, m, d,
		timeFormatPatternPrefix+indiaMarketEndTime, time.RFC3339, marketEndTimeCalcFailureErrorMessage)

	return marketStartTime, marketEndTime
}

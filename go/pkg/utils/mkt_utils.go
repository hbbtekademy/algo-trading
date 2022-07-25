package utils

import (
	"fmt"
	"log"
	"time"
)

/*
This struct will capture all attributes specific to the market
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

/* TODO: Refactor - MarketUtils must know the start and end time of the market.
Caller must provide an unique value corresponding to a market and MarketUtils must return
a MarketSpecifications struct with all required specifications
*/
func NewMktUtil(mst time.Time, met time.Time) *MarketSpecifications {
	return &MarketSpecifications{
		marketStartTime: mst,
		marketEndTime:   met,
	}
}

func (m *MarketSpecifications) IsValidMarketHrs(t time.Time) bool {
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
	mst, err := time.Parse(time.RFC3339, fmt.Sprintf("%d-%02d-%02dT08:59:59+05:30", y, int(m), d))
	if err != nil {
		log.Fatalln("failed getting market start time:", err)
	}

	met, err := time.Parse(time.RFC3339, fmt.Sprintf("%d-%02d-%02dT16:00:00+05:30", y, int(m), d))
	if err != nil {
		log.Fatalln("failed getting market end time:", err)
	}

	return mst, met
}

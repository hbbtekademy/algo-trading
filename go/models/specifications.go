package models

import "time"

/*
MarketSpecifications - This struct will capture all attributes specific to the market
marketStartTime - Local time when the market opens
marketEndTime - Local time when the market closes
marketStartTimeUTC - UTC time when the market opens
marketEndTimeUTC - UTC time when the market closes
marketName - NSE,BSE,NYSE,NASDAQ,CME,Binance,FX
isMarket247 -set to true when the market is always open
*/
type Specifications struct {
	MarketStartTime time.Time
	MarketEndTime   time.Time
}

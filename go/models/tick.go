package models

import "time"

// Tick TODO: Rename to CBTick ? Where CB = Chartbusters
type Tick struct {
	InstrumentToken    uint32
	Sym                string
	ExchangeTS         time.Time
	LastTradeTS        time.Time
	LTP                float32
	LastTradedQuantity uint32
	VolumeTraded       uint32
}

type OHLCV struct {
	Open   float32
	High   float32
	Low    float32
	Close  float32
	Volume uint32
}

type Candle struct {
	TS              time.Time
	InstrumentToken uint32
	Sym             string
	OHLCV           *OHLCV
}

package models

type Instrument struct {
	Id      uint32
	Sym     string
	LotSize int
}

type Instruments map[uint32]*Instrument

package models

type Instrument struct {
	Id  uint32
	Sym string
}

type Instruments map[uint32]*Instrument

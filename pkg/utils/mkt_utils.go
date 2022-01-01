package utils

import (
	"fmt"
	"log"
	"time"
)

type Mktutil struct {
	mst time.Time
	met time.Time
}

func NewMktUtil(mst time.Time, met time.Time) *Mktutil {
	return &Mktutil{
		mst: mst,
		met: met,
	}
}

func (m *Mktutil) GetMarketTime() (time.Time, time.Time) {
	return m.mst, m.met
}

func (m *Mktutil) IsValidMarketHrs(t time.Time) bool {
	return t.After(m.mst) && t.Before(m.met)
}

func (m *Mktutil) IsAfterMarketHrs(t time.Time) bool {
	return t.After(m.met)
}

func (m *Mktutil) IsBeforeMarketHrs(t time.Time) bool {
	return t.Before(m.mst)
}

func GetMarketTime() (time.Time, time.Time) {
	y, m, d := time.Now().Date()
	mst, err := time.Parse(time.RFC3339, fmt.Sprintf("%d-%02d-%02dT09:14:59+05:30", y, int(m), d))
	if err != nil {
		log.Fatalln("failed getting market start time:", err)
	}

	met, err := time.Parse(time.RFC3339, fmt.Sprintf("%d-%02d-%02dT15:30:00+05:30", y, int(m), d))
	if err != nil {
		log.Fatalln("failed getting market end time:", err)
	}

	return mst, met
}

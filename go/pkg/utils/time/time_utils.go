package time

import (
	"fmt"
	"log"
	"time"
)

func GetTime(y int, m time.Month, d int, timeAsString string, timeLayout string, logMessage string) time.Time {
	timeObject, err := time.Parse(timeLayout, fmt.Sprintf(timeAsString, y, int(m), d))
	if err != nil {
		log.Fatalln(logMessage, err)
	}
	return timeObject
}

package instruments_repository

import "org.hbb/algo-trading/go/models"

// GetAllAngleOneInstruments TODO: Need list of instruments from Sameer for MVP
func GetAllAngleOneInstruments() models.Instruments {
	instruments := make(models.Instruments)
	instruments[1594] = &models.Instrument{Id: 1594, Sym: "NSE_CM"}
	instruments[44476] = &models.Instrument{Id: 44476, Sym: "NIFTY11AUG2216150PE"}
	instruments[0] = &models.Instrument{Id: 0, Sym: "BAD_DATA"}
	return instruments
}

package angel_one

import (
	"log"
	"testing"
)

func TestMapAngelOneTickToCBTickNilData(t *testing.T) {
	t.Parallel()
	m := make(map[string]interface{})
	m["tk"] = nil
	m["e"] = nil
	m["ltt"] = nil
	m["ltp"] = nil
	m["ltq"] = nil
	m["v"] = nil
	cbTick := mapAngelOneTickToCBTick(m)
	log.Print("cbTick", cbTick)
}

func TestMapAngelOneTickToCBTick(t *testing.T) {
	t.Parallel()
	cbTick := mapAngelOneTickToCBTick(getMessage())
	log.Print("cbTick", cbTick)
}

func getMessage() map[string]interface{} {
	m := make(map[string]interface{})
	// Source : https://smartapi.angelbroking.com/docs/WebSocketStreaming
	m["name"] = "sf"
	m["tk"] = "1594"
	m["e"] = "nse_cm"
	m["ltp"] = "1621.40"
	m["c"] = "C"
	m["nc"] = "NC"
	m["cng"] = "CNG"
	m["v"] = "1000000"
	m["bq"] = "BQ"
	m["bp"] = "BP"
	m["bs"] = "BS"
	m["sp"] = "SP"
	m["ltq"] = "1000"
	m["ltt"] = "05/08/2022 11:17:46"
	m["ucl"] = "UCL"
	m["tbq"] = "TBQ"
	m["mc"] = "MC"
	m["lo"] = "LO"
	m["yh"] = "YH"
	m["op"] = "OP"
	m["ts"] = "TS"
	m["h"] = "H"
	m["lcl"] = "LCL"
	m["tsq"] = "TSQ"
	m["ap"] = "AP"
	m["yl"] = "YL"
	m["h"] = "H"
	m["oi"] = "OI"
	m["isdc"] = "ISDC"
	m["to"] = "TO"
	m["toi"] = "TOI"
	m["lter"] = "LTER"
	m["hter"] = "HTER"
	m["setltyp"] = "SETLTYP"
	return m
}

package main

import (
	"io/ioutil"
	"log"
	"os"
	"strconv"
	"strings"
)

var (
	instruments map[int]string
)

// TODO: need to read through this
func main() {
	initInstruments()
	baseDir := "/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/20211217"
	files, err := ioutil.ReadDir(baseDir)
	if err != nil {
		log.Fatalln(err)
	}

	for _, f := range files {
		//log.Println(f.Name())
		i := strings.Split(f.Name(), "-")[0]
		id, _ := strconv.Atoi(i)
		sym := instruments[id]
		log.Println("Instrument: " + sym)
		err := os.Rename(baseDir+"/"+f.Name(), baseDir+"/"+sym+"-20211217.csv")
		if err != nil {
			return
		}
	}
}

func initInstruments() {
	if instruments == nil {
		instruments = make(map[int]string)
	}
	instruments[5633] = "ACC"
	instruments[6401] = "ADANIENT"
	instruments[912129] = "ADANIGREEN"
	instruments[3861249] = "ADANIPORTS"
	instruments[2616577] = "ADANITRANS-BE"
	instruments[325121] = "AMBUJACEM"
	instruments[40193] = "APOLLOHOSP"
	instruments[60417] = "ASIANPAINT"
	instruments[70401] = "AUROPHARMA"
	instruments[5097729] = "DMART"
	instruments[1510401] = "AXISBANK"
	instruments[4267265] = "BAJAJ-AUTO"
	instruments[81153] = "BAJFINANCE"
	instruments[4268801] = "BAJAJFINSV"
	instruments[78081] = "BAJAJHLDNG"
	instruments[579329] = "BANDHANBNK"
	instruments[1195009] = "BANKBARODA"
	instruments[103425] = "BERGEPAINT"
	instruments[134657] = "BPCL"
	instruments[2714625] = "BHARTIARTL"
	instruments[2911489] = "BIOCON"
	instruments[558337] = "BOSCHLTD"
	instruments[140033] = "BRITANNIA"
	instruments[2029825] = "CADILAHC"
	instruments[175361] = "CHOLAFIN"
	instruments[177665] = "CIPLA"
	instruments[5215745] = "COALINDIA"
	instruments[3876097] = "COLPAL"
	instruments[197633] = "DABUR"
	instruments[2800641] = "DIVISLAB"
	instruments[3771393] = "DLF"
	instruments[225537] = "DRREDDY"
	instruments[232961] = "EICHERMOT"
	instruments[1207553] = "GAIL"
	instruments[303617] = "GLAND"
	instruments[2585345] = "GODREJCP"
	instruments[315393] = "GRASIM"
	instruments[2513665] = "HAVELLS"
	instruments[1850625] = "HCLTECH"
	instruments[340481] = "HDFC"
	instruments[1086465] = "HDFCAMC"
	instruments[341249] = "HDFCBANK"
	instruments[119553] = "HDFCLIFE"
	instruments[345089] = "HEROMOTOCO"
	instruments[348929] = "HINDALCO"
	instruments[359937] = "HINDPETRO"
	instruments[356865] = "HINDUNILVR"
	instruments[1270529] = "ICICIBANK"
	instruments[5573121] = "ICICIGI"
	instruments[4774913] = "ICICIPRULI"
	instruments[415745] = "IOC"
	instruments[2883073] = "IGL"
	instruments[7458561] = "INDUSTOWER"
	instruments[1346049] = "INDUSINDBK"
	instruments[3520257] = "NAUKRI"
	instruments[408065] = "INFY"
	instruments[2865921] = "INDIGO"
	instruments[424961] = "ITC"
	instruments[1723649] = "JINDALSTEL"
	instruments[3001089] = "JSWSTEEL"
	instruments[4632577] = "JUBLFOOD"
	instruments[492033] = "KOTAKBANK"
	instruments[4561409] = "LTI"
	instruments[2939649] = "LT"
	instruments[2672641] = "LUPIN"
	instruments[519937] = "M&M"
	instruments[1041153] = "MARICO"
	instruments[2815745] = "MARUTI"
	instruments[6054401] = "MUTHOOTFIN"
	instruments[4598529] = "NESTLEIND"
	instruments[3924993] = "NMDC"
	instruments[2977281] = "NTPC"
	instruments[633601] = "ONGC"
	instruments[6191105] = "PIIND"
	instruments[681985] = "PIDILITIND"
	instruments[617473] = "PEL"
	instruments[3834113] = "POWERGRID"
	instruments[240641] = "PGHL"
	instruments[2730497] = "PNB"
	instruments[738561] = "RELIANCE"
	instruments[4600577] = "SBICARD"
	instruments[5582849] = "SBILIFE"
	instruments[794369] = "SHREECEM"
	instruments[806401] = "SIEMENS"
	instruments[779521] = "SBIN"
	instruments[758529] = "SAIL"
	instruments[857857] = "SUNPHARMA"
	instruments[2953217] = "TCS"
	instruments[878593] = "TATACONSUM"
	instruments[884737] = "TATAMOTORS"
	instruments[895745] = "TATASTEEL"
	instruments[3465729] = "TECHM"
	instruments[897537] = "TITAN"
	instruments[900609] = "TORNTPHARM"
	instruments[2952193] = "ULTRACEMCO"
	instruments[2674433] = "MCDOWELL-N"
	instruments[2889473] = "UPL"
	instruments[784129] = "VEDL"
	instruments[969473] = "WIPRO"
	instruments[3050241] = "YESBANK"
}

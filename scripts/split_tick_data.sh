#!/bin/sh

validateInput() {
   echo "Validating input $@ $1"
   if [ -z $1 ]
   then
      echo "Enter date in yyyymmdd format"
      exit 1
   fi
}

validateInput $@

date=$1
masterTickData="../../TickData/$date/Ticker-$date.csv"
header="Symbol,ExcTS,LastTradeTS,LastPrice,LastTradedQty,VolumeTraded"
file $masterTickData

# Loop over the master instrument list and split each instruments tick data into a separate file
while read i; do
   echo "Splitting tick data for instrument: $i"
   
   ii=`echo $i | sed -e "s/,//g"`
   splitFN="../../TickData/$date/$ii-$date.csv"
   
   echo $header > $splitFN
   grep $i $masterTickData >> $splitFN &
done < instrument_symbol.txt

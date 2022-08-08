package event_handler

import (
	"log"
	"strconv"
	"time"

	"org.hbb/algo-trading/go/models"
)

//Observed market tick data is received after market close. Buffer time need to collate these ticks.
const bufferTimeToCollectAfterMarketHoursTickData = -5

func ConsumeTick(tick *models.Tick, marketSpecifications *models.MarketSpecifications, channelClosed bool,
	fileTickChannel chan *models.Tick, redisTickChannel chan *models.Tick) {
	if checkAndCloseAllChannels(marketSpecifications, channelClosed, fileTickChannel, redisTickChannel) {
		return
	}
	if checkAndLogTicksReceivedAfterMarketClose(tick, marketSpecifications) {
		return
	}
	streamTicksToChannels(tick, channelClosed, fileTickChannel, redisTickChannel)
}

func streamTicksToChannels(tick *models.Tick, channelClosed bool, fileTickChannel chan *models.Tick, redisTickChannel chan *models.Tick) {
	if !channelClosed {
		fileTickChannel <- tick
		redisTickChannel <- tick
	}
}

func checkAndLogTicksReceivedAfterMarketClose(tick *models.Tick, marketSpecifications *models.MarketSpecifications) bool {
	if !marketSpecifications.IsMarketOpen(tick.ExchangeTS) {
		//Safety - Are we receiving ticks after close of market/
		log.Printf("ExchangeTS: %s outside mkt hrs. Skip tick for Sym %s",
			tick.ExchangeTS.Format(time.RFC3339), strconv.Itoa(int(tick.InstrumentToken)))
		return true
	}
	return false
}

func checkAndCloseAllChannels(marketSpecifications *models.MarketSpecifications, channelClosed bool,
	fileTickChannel chan *models.Tick, redisTickChannel chan *models.Tick) bool {
	if marketSpecifications.IsAfterMarketHrs(getCurrentTimeWithBuffer()) && !channelClosed {
		log.Printf("Current Time: %s after mkt hrs. Closing File and Redis channels...",
			time.Now().Format(time.RFC3339))
		if !channelClosed {
			//Market Closed. Close all channels.
			close(fileTickChannel)
			close(redisTickChannel)
			channelClosed = true
		}
		return true
	}
	return false
}

func getCurrentTimeWithBuffer() time.Time {
	return time.Now().Add(bufferTimeToCollectAfterMarketHoursTickData * time.Minute)
}

from typing import Tuple

from python.chartbusters.model.cb_candle import CBCandle
from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v1 import CBSignalV1
from python.chartbusters.strategies.cb_strategy import CBStrategy
from python.chartbusters.util import constants


class CBBuyStrategy(CBStrategy):
    def __init__(self, chart: CBChart) -> None:
        super().__init__(chart)

    def rsi_filter(self, candle: CBCandle, rsi: float) -> bool:
        prev_candle = self.chart.previous(candle)
        return candle.rsi >= rsi > prev_candle.rsi

    def stop_loss_filter(self, candle: CBCandle, stop_loss: float) -> Tuple[bool, float]:
        prev_candle = self.chart.previous(candle)
        return ((candle.high - prev_candle.low) * self.chart.lot_size <= stop_loss), prev_candle.low

    def generate_signal_pnl(self, signal: CBSignalV1, stop_gain: float) -> None:
        df = self.chart.df[signal.ts:].copy()
        df.drop(index=df.index[0], axis=0, inplace=True)
        rnum = 0

        for index, row in df.iterrows():
            adx = row[constants.ADX]
            if row[constants.LOW] < signal.stop_loss:
                # print('rnum: {}, index: {}, low: {}, sl: {}'.format(rnum, index, row['Low'], signal.stop_loss))
                signal.pnl = -1 * (signal.entry_price -
                                   signal.stop_loss) * signal.lot_size
                signal.exit_ts = index
                signal.exit_price = signal.stop_loss
                signal.comment = "Stop Loss Breached at {}".format(index)
                break

            if (row[constants.HIGH] - signal.entry_price) * signal.lot_size >= stop_gain:
                signal.pnl = stop_gain
                signal.exit_ts = index
                signal.exit_price = round(
                    stop_gain/signal.lot_size + signal.entry_price, 2)
                signal.comment = "Stop Gain reached at {}".format(index)
                break

            if rnum > 50:
                signal.pnl = (row[constants.CLOSE] -
                              signal.entry_price) * signal.lot_size
                signal.exit_ts = index
                signal.exit_price = row[constants.CLOSE]
                signal.comment = "Signal failed to generate {}".format(index)
                break

            rnum = rnum+1

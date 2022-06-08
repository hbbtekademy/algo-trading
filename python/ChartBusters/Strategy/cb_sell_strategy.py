from typing import Tuple
from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_candle import CBCandle
from ChartBusters.cb_signal import CBSignal
from ChartBusters.Strategy.cb_strategy import CBStrategy
from ChartBusters.Strategy.cb_backtest_result import CBBackTestResult
from ChartBusters import constants


class CBSellStrategy(CBStrategy):
    def __init__(self, chart: CBChart) -> None:
        super().__init__(chart)

    def rsi_filter(self, candle: CBCandle, rsi: float) -> bool:
        prev_candle = self.chart.previous(candle)
        return candle.rsi <= rsi < prev_candle.rsi

    def stop_loss_filter(self, candle: CBCandle, stop_loss: float) -> Tuple[bool, float]:
        prev_candle = self.chart.previous(candle)
        return ((prev_candle.high - candle.low) * self.chart.lot_size <= stop_loss), prev_candle.high

    def generate_signal_pnl(self, signal: CBSignal, stop_gain: float) -> None:
        df = self.chart.df[signal.ts:].copy()
        df.drop(index=df.index[0], axis=0, inplace=True)
        rnum = 0
        for index, row in df.iterrows():
            if row[constants.HIGH] > signal.stop_loss:
                # print('rnum: {}, index: {}, low: {}, sl: {}'.format(rnum, index, row['Low'], signal.stop_loss))
                signal.pnl = (signal.entry_price -
                              signal.stop_loss) * signal.lot_size
                signal.exit_ts = index
                signal.exit_price = signal.stop_loss
                signal.comment = "Stop Loss Breached at {}".format(index)
                break

            if (signal.entry_price - row[constants.LOW]) * signal.lot_size >= stop_gain:
                signal.pnl = stop_gain
                signal.exit_ts = index
                signal.exit_price = round(
                    signal.entry_price - stop_gain/signal.lot_size, 2)
                signal.comment = "Stop Gain reached at {}".format(index)
                break

            if rnum > 50:
                signal.pnl = (signal.entry_price -
                              row[constants.CLOSE]) * signal.lot_size
                signal.exit_ts = index
                signal.exit_price = row[constants.CLOSE]
                # print('Signal failed to generate PnL: {}'.format(signal.pnl))
                signal.comment = "Signal failed to generate {}".format(index)
                break
        # @HBB - Can we remove the below?
        rnum = rnum+1

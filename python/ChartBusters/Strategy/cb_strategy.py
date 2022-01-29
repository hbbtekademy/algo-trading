from typing import Tuple
from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_candle import CBCandle
from ChartBusters.cb_signal import CBSignal
from ChartBusters.Strategy.cb_backtest_result import CBBackTestResult
from ChartBusters import constants


class CBStrategy():
    def __init__(self, chart: CBChart) -> None:
        self.chart = chart

    def adx_filter(self, candle: CBCandle, adx_min: float, adx_max: float) -> bool:
        return (candle.adx >= adx_min and candle.adx <= adx_max)

    def execute(candle: CBCandle):
        pass

    def generate_signal_pnl(self, signal: CBSignal, stop_gain: float) -> None:
        pass

    def back_test(self, start_ts, end_ts) -> CBBackTestResult:
        signals = list()
        candles = self.chart.sub_chart(start_ts, end_ts)
        for candle in candles:
            result = self.execute(candle)
            if (result.passed):
                signal = CBSignal(self.strategy, self.chart.sym, self.chart.lot_size, candle.ts,
                                  result.entry_price, result.stop_loss, candle)
                self.generate_signal_pnl(signal, self.stop_gain)
                signals.append(signal)

        btResult = CBBackTestResult(self.chart.sym, signals)
        return btResult

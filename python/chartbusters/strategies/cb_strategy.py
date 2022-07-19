from python.chartbusters.model.cb_candle import CBCandle
from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v1 import CBSignalV1
from python.chartbusters.strategies.cb_backtest_result import CBBackTestResult


class CBStrategy:
    def __init__(self, chart: CBChart) -> None:
        self.chart = chart

    @staticmethod
    def adx_filter(candle: CBCandle, adx_min: float, adx_max: float) -> bool:
        return adx_min <= candle.adx <= adx_max

    def execute(self, candle: CBCandle, signal: CBSignalV1):
        pass

    def generate_signal_pnl(self, signal: CBSignalV1, stop_gain: float) -> None:
        pass

    def back_test(self, start_ts, end_ts) -> CBBackTestResult:
        signals = list()
        candles = self.chart.sub_chart(start_ts, end_ts)
        for candle in candles:
            result = self.execute(candle)
            if result.passed:
                signal = CBSignalV1(self.strategy, self.chart.sym, self.chart.lot_size, candle.ts,
                                    result.entry_price, result.stop_loss, candle)
                self.generate_signal_pnl(signal, self.stop_gain)
                signals.append(signal)

        bt_result = CBBackTestResult(self.chart.sym, signals)
        return bt_result

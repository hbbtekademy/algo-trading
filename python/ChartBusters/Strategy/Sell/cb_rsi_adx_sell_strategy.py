from typing import List, Tuple
from ChartBusters.Strategy.cb_sell_strategy import CBSellStrategy
from ChartBusters.Strategy.cb_strategy_result import CBStrategyResult
from ChartBusters.Strategy.cb_backtest_result import CBBackTestResult
from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_candle import CBCandle
from ChartBusters.cb_signal import CBSignal


class RSI_ADX_Sell_Strategy(CBSellStrategy):
    def __init__(self, chart: CBChart, stop_loss: float, stop_gain: float, rsi_filter: float = 70, adx_min: float = 30, adx_max: float = 40) -> None:
        super().__init__(chart)
        self.strategy = 'RSI_ADX_Sell'
        self.stop_loss = stop_loss
        self.stop_gain = stop_gain
        self._rsi_filter = rsi_filter
        self.adx_min = adx_min
        self.adx_max = adx_max

    def execute(self, candle: CBCandle) -> CBStrategyResult:
        rsi_pass = False
        adx_pass = False
        sl_pass = False

        rsi_pass = self.rsi_filter(candle, self._rsi_filter)
        adx_pass = self.adx_filter(candle, self.adx_min, self.adx_max)
        sl_pass, sl = self.stop_loss_filter(candle, self.stop_loss)

        passed = (rsi_pass and adx_pass and sl_pass)
        entry_price = 0
        stop_loss = 0

        if passed:
            entry_price = candle.low
            stop_loss = sl

        result = CBStrategyResult(passed, entry_price, stop_loss)

        return result

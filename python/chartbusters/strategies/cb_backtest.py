from typing import List

from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v1 import CBSignalV1
from python.chartbusters.strategies.cb_strategy import CBStrategy


class CBBackTest:
    def __init__(self, chart: CBChart, strategy: CBStrategy) -> None:
        self.chart = chart
        self.strategy = strategy

    def back_test(self, start_ts, end_ts) -> List[CBSignalV1]:
        all_signals = list()

        signal = CBSignalV1('', '', 0, '', 0, 0, None)
        # what are the various signal statuses?
        # X = No Signal
        signal.status = 'X'

        candles = self.chart.sub_chart(start_ts, end_ts)
        for candle in candles:
            sig_type, new_signal = self.strategy.execute(candle, signal)
            if sig_type == 'New' and new_signal.is_not_eod_signal:
                all_signals.append(new_signal)
                signal = new_signal
            if sig_type == 'PSig':
                signal = new_signal
            if sig_type == 'SL':
                signal = CBSignalV1('', '', 0, '', 0, 0, None)
                signal.status = 'X'

        return all_signals

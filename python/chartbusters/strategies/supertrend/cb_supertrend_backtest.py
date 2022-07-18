from typing import List

from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v1 import CBSignalV1
from python.chartbusters.strategies.cb_strategy import CBStrategy


class CBSuperTrendBackTest:
    def __init__(self, chart: CBChart, strategy: CBStrategy) -> None:
        self.chart15 = chart
        self.strategy15 = strategy

    def back_test(self, start_ts, end_ts) -> List[CBSignalV1]:
        all_signals15 = list()

        signal = CBSignalV1('', '', 0, '', 0, 0, None)
        signal.status = 'X'

        candles = self.chart15.sub_chart(start_ts, end_ts)
        hourly_index = None
        for candle in candles:
            hourly_index = candle.ts if candle.is_start_of_hr() else hourly_index
            sig_type, new_signal = self.strategy15.execute(candle, signal)
            if sig_type == 'New' and new_signal.is_eod_signal() is not True:
                # print('Adding new signal ', candle.ts)
                all_signals15.append(new_signal)
                signal = new_signal
            if sig_type == 'PSig':
                signal = new_signal
            if sig_type == 'SL':
                signal = CBSignalV1('', '', 0, '', 0, 0, None)
                signal.status = 'X'

        return all_signals15

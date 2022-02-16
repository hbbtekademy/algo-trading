from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_candle import CBCandle
from ChartBusters.cb_signal import CBSignal
from ChartBusters.Strategy.cb_supertrend_strategy import CBSuperTrendStrategy
from ChartBusters.Strategy.cb_supertrend_strategy_v1 import CBSuperTrendStrategyV1
from typing import List, Tuple


class CBSuperTrendBackTest():
    def __init__(self, chart15: CBChart, chart60: CBChart, expiry,
                 stoploss_margin15: int = 120, stoploss_margin60: int = 180,
                 supertrend_ma_margin: int = 50, stoploss_gap: int = 20) -> None:
        self.chart15 = chart15
        self.chart60 = chart60
        self.expiry = expiry
        # self.stoploss_margin = stoploss_margin
        self.strategy15 = CBSuperTrendStrategy('SuperTrend15',
                                               chart15, expiry, stoploss_margin=stoploss_margin15,
                                               supertrend_ma_margin=supertrend_ma_margin, stoploss_gap=stoploss_gap)
        self.strategy60 = CBSuperTrendStrategy('SuperTrend60',
                                               chart60, expiry, stoploss_margin=stoploss_margin60,
                                               supertrend_ma_margin=supertrend_ma_margin, stoploss_gap=stoploss_gap)

    def back_test(self, start_ts, end_ts) -> Tuple[List[CBSignal], List[CBSignal]]:
        all_signals15 = list()
        all_signals60 = list()

        signal = CBSignal('', '', 0, '', 0, 0, None)
        signal.status = 'X'
        signal60 = CBSignal('', '', 0, '', 0, 0, None)
        candles = self.chart15.sub_chart(start_ts, end_ts)
        hourly_index = None
        for candle in candles:
            hourly_index = candle.ts if candle.is_start_of_hr() else hourly_index
            sig_type, new_signal = self.strategy15.execute(candle, signal)
            if (sig_type == 'New' and new_signal.is_eod_signal() != True):
                # print('Adding new signal ', candle.ts)
                all_signals15.append(new_signal)
                signal = new_signal
            if (sig_type == 'PSig'):
                signal = new_signal
            if(sig_type == 'SL'):
                signal = CBSignal('', '', 0, '', 0, 0, None)
                signal.status = 'X'

            hourly_index = None
            if(hourly_index != None and candle.is_end_of_hr()):
                # print('15 min signal still open. Run hourly strategy')
                # print(hourly_index, len(all_signals15),all_signals15[-1].status)
                candle60 = self.chart60.candle(hourly_index)
                sig_type60, new_signal60 = self.strategy60.execute(
                    candle60, signal60)
                if (sig_type60 == 'New'):
                    all_signals60.append(new_signal60)
                    signal60 = new_signal60
                if (sig_type60 == 'PSig'):
                    # print('PSignal generated on hourly strategy. TS:{}'.format(new_signal60.ts))
                    signal60 = new_signal60
                if(sig_type60 == 'SL'):
                    signal60 = CBSignal('', '', 0, '', 0, 0, None)

            elif(hourly_index != None and candle.is_end_of_hr() and len(all_signals15) > 0 and all_signals15[-1].status == 'C'):
                sig_15_ts = all_signals15[-1].ts
                sig_15_pnl = all_signals15[-1].pnl
                # print('15 min signal {} closed at PnL {}. Skip hourly strategy {}'.format(sig_15_ts, sig_15_pnl, hourly_index))

        return (all_signals15, all_signals60)

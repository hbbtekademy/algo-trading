from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_candle import CBCandle
from ChartBusters.cb_signal import CBSignal
from ChartBusters.Strategy.cb_supertrend_strategy import CBSuperTrendStrategy
from ChartBusters.Strategy.cb_supertrend_strategy_v1 import CBSuperTrendStrategyV1
from typing import List, Tuple


class CBSuperTrendBackTest():
    def __init__(self, chart15: CBChart, chart60: CBChart, expiry, rsi: float = 30, close_margin: int = 50, stoploss_margin: int = 10) -> None:
        self.chart15 = chart15
        self.chart60 = chart60
        self.expiry = expiry
        self.rsi = rsi
        self.close_margin = close_margin
        self.stoploss_margin = stoploss_margin
        self.strategy15 = CBSuperTrendStrategy(
            chart15, expiry, rsi=rsi, close_margin=close_margin, stoploss_margin=stoploss_margin)
        self.strategy60 = CBSuperTrendStrategy(
            chart60, expiry, rsi=rsi, close_margin=close_margin, stoploss_margin=stoploss_margin)

    def back_test(self, start_ts, end_ts) -> Tuple[List[CBSignal], List[CBSignal]]:
        all_signals15 = list()
        all_signals60 = list()

        signal = CBSignal('', '', 0, '', 0, 0, None)
        signal60 = CBSignal('', '', 0, '', 0, 0, None)
        candles = self.chart15.sub_chart(start_ts, end_ts)
        hourly_index = None
        for candle in candles:
            hourly_index = candle.ts if candle.is_start_of_hr() else hourly_index
            sig_type, new_signal = self.strategy15.execute(candle, signal)
            if (sig_type == 'New'):
                all_signals15.append(new_signal)
                signal = new_signal
            if(sig_type == 'SL'):
                signal = CBSignal('', '', 0, '', 0, 0, None)

            if(hourly_index != None and candle.is_end_of_hr() and
               ((len(all_signals15) > 0 and all_signals15[-1].status == 'O') or (len(all_signals60) > 0 and all_signals60[-1].status == 'O'))):
                # print('15 min signal still open. Run hourly strategy')
                # print(hourly_index)
                candle60 = self.chart60.candle(hourly_index)
                sig_type60, new_signal60 = self.strategy60.execute(
                    candle60, signal60)
                if (sig_type60 == 'New'):
                    all_signals60.append(new_signal60)
                    signal60 = new_signal60
                if(sig_type60 == 'SL'):
                    signal60 = CBSignal('', '', 0, '', 0, 0, None)

            elif(hourly_index != None and candle.is_end_of_hr() and len(all_signals15) > 0 and all_signals15[-1].status == 'C'):
                sig_15_ts = all_signals15[-1].ts
                sig_15_pnl = all_signals15[-1].pnl
                # print('15 min signal {} closed at PnL {}. Skip hourly strategy {}'.format(sig_15_ts, sig_15_pnl, hourly_index))

        return (all_signals15, all_signals60)

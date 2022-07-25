from unittest import TestCase

import pandas as pd

from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v1 import CBSignalV1
from python.chartbusters.strategies.supertrend.basic.cb_supertrend_strategy import CBSuperTrendStrategy


class TestCBSuperTrendStrategy(TestCase):

    def setUp(self) -> None:
        file = self.get_test_data_file()
        df = self.get_data_frame(file)
        cb_chart = self.get_cb_chart(df)
        self.class_under_test = self.get_strategy(cb_chart)

    @staticmethod
    def get_strategy(cb_chart):
        return CBSuperTrendStrategy('SuperTrend15',
                                    cb_chart, '2022-06-30',
                                    stoploss_margin=120,
                                    supertrend_ma_margin=50,
                                    stoploss_gap=20)

    @staticmethod
    def get_cb_chart(self, df):
        return CBChart('NIFTY22JUNFUT', 50
                       , df, ema_interval=31,
                       sma_interval=29,
                       MA='EMA',
                       sti_interval=11,
                       sti_multiplier=2)

    @staticmethod
    def get_data_frame(self, file):
        return pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])

    @staticmethod
    def get_test_data_file(self):
        return './data/NIFTY22JUNFUT-HIST-15M.csv'

    def test_clean_buy_signal_generation(self):
        start_ts = '2022-05-25'
        end_ts = '2022-07-01'
        signal = CBSignalV1('', '', 0, '', 0, 0, None)
        # what are the various signal statuses?
        # X = No Signal
        signal.status = 'X'
        candles = self.class_under_test.chart.sub_chart(start_ts, end_ts)
        for candle in candles:
            sig_type, new_signal = self.class_under_test.execute(candle, signal)

    def test_clean_sell_signal_generation(self):
        pass

    def test_potential_buy_signal_generation(self):
        pass

    def test_potential_sell_signal_generation(self):
        pass

    def test_potential_buy_converting_to_clean_buy_signal_with_ema_completely_below_candle_generation(self):
        pass

    def test_potential_sell_converting_to_clean_sell_signal_with_ema_completely_above_candle_generation(self):
        pass

    def test_potential_buy_converting_to_clean_buy_signal_with_ema_50percent_logic_generation(self):
        pass

    def test_potential_sell_converting_to_clean_sell_signal_with_ema_50percent_logic_generation(self):
        pass

    def test_stoploss_switches_when_ema_goes_below_sti(self):
        pass

    def test_stoploss_switches_when_sti_goes_below_ema(self):
        pass

    def test_when_diff_between_stoploss_and_ema_more_than50_then_stoploss_revised(self):
        pass

    def test_when_stoploss_hit_then_trade_close_signal_generated(self):
        pass


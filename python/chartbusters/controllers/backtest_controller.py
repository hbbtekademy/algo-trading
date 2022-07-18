import pandas as pd

from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v1 import CBSignalV1
from python.chartbusters.strategies.supertrend.basic.cb_supertrend_strategy import CBSuperTrendStrategy
from python.chartbusters.strategies.supertrend.cb_supertrend_backtest import CBSuperTrendBackTest
from python.chartbusters.util import constants


class BacktestExecutor:

    def __init__(self, driver_file):
        self.driver_file = driver_file
        '''
        TODO: these constants are specific to each strategies but also needs to be passed to 
        the CBChart class which is agnostic to the strategies. Need to design this better.
        '''
        self.ema_interval = 31
        self.sma_interval = 29
        self.MA = constants.EMA
        self.supertrend_ma_margin = 50
        self.stoploss_gap = 20
        self.sti_interval = 11
        self.sti_multiplier = 2

    def connect(self):
        pass

    def execute_strategy(self):
        pass

    def calculate_pnl(self):
        pass

    def broadcast_result(self):
        print('b result')

    def execute(self, message) -> str:
        print('exec', message)
        all_signals = list()
        driver_file = self.get_driver_file()

        for index, row in driver_file.iterrows():
            lot_size = int(row['LotSize'])
            expiry = row['Expiry']
            stoploss_margin = int(row['StopLoss15'])
            backtest_start = row['Start'].tz_localize('Asia/Kolkata')
            backtest_end = row['End'].tz_localize('Asia/Kolkata')
            file = self.get_hist_data_filename(index)
            df = self.get_historical_data(file)
            cb_chart = self.get_cbchart(df, index, lot_size)
            strategy = self.get_strategy(row, cb_chart)
            backtest = self.get_backtest(row, cb_chart, strategy)
            signals15 = backtest.back_test(row['Start'].tz_localize('Asia/Kolkata'),
                                           row['End'].tz_localize('Asia/Kolkata'))
            total_monthly_pnl = self.calc_total_monthly_pnl(all_signals, signals15)

        print('{}'.format(total_monthly_pnl))

        total_pnl, total_count = self.calc_total_pnl_and_count(all_signals)

        print(" ")
        print(" ")
        print("Total PnL,{},Total Trades,{}".format(total_pnl, total_count * 2))

        return 'total_pnl'

    def get_driver_file(self):
        driver_file = pd.read_csv(self.driver_file, parse_dates=['Start', 'End'], index_col=['Sym'])
        return driver_file

    @staticmethod
    def calc_total_pnl_and_count(all_signals):
        total_pnl = 0
        total_count = 0
        CBSignalV1.print_header()
        for signal in all_signals:
            total_pnl = total_pnl + signal.pnl
            total_count = total_count + 1
            signal.pretty_print()
        return total_pnl, total_count

    @staticmethod
    def calc_total_monthly_pnl(all_signals, signals15):
        total_monthly_pnl = 0
        for s in signals15:
            total_monthly_pnl = total_monthly_pnl + s.pnl
            all_signals.append(s)
        return total_monthly_pnl

    @staticmethod
    def get_historical_data(file):
        df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])
        return df

    @staticmethod
    def get_backtest(row, cb_chart, strategy):
        return CBSuperTrendBackTest(cb_chart, strategy)

    @staticmethod
    def get_hist_data_filename(index):
        file = './backtest/hist15min/' + index + '-HIST-15M.csv'
        return file

    def get_strategy(self, row, cb_chart):
        return CBSuperTrendStrategy('SuperTrend15',
                                    cb_chart, row['Expiry'],
                                    stoploss_margin=int(row['StopLoss15']),
                                    supertrend_ma_margin=self.supertrend_ma_margin, stoploss_gap=self.stoploss_gap)

    def get_cbchart(self, df, symbol, lot_size):
        return CBChart(symbol, lot_size
                       , df, ema_interval=self.ema_interval, sma_interval=self.sma_interval, MA=self.MA,
                       sti_interval=self.sti_interval,
                       sti_multiplier=self.sti_multiplier)

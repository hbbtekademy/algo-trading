import pandas as pd

from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v1 import CBSignalV1
from python.chartbusters.strategies.cb_backtest import CBBackTest
from python.chartbusters.strategies.rsi.cb_rsi_adx_buy_or_sell_strategy import RsiAdxBuyOrSellStrategy
from python.chartbusters.strategies.supertrend.basic.cb_supertrend_strategy import CBSuperTrendStrategy


class BacktestExecutor:

    def __init__(self, driver_file, strategy_params_dict):
        self.driver_file = driver_file
        self.strategy_params_dict = strategy_params_dict

    def connect(self):
        pass

    def execute_strategy(self):
        pass

    def calculate_pnl(self):
        pass

    def broadcast_result(self):
        print('b result')

    def execute(self, strategy_name) -> str:
        all_signals = list()
        driver_file = self.get_driver_file()
        total_monthly_pnl = 0

        for index, row in driver_file.iterrows():
            lot_size = int(row['LotSize'])
            backtest_start = row['Start'].tz_localize('Asia/Kolkata')
            backtest_end = row['End'].tz_localize('Asia/Kolkata')

            df = self.get_historical_data(self.get_hist_data_filename(index))
            cb_chart = self.get_cbchart(df, index, lot_size, strategy_name)
            strategy = self.get_strategy(row, cb_chart, strategy_name)
            backtest = self.get_backtest(cb_chart, strategy, strategy_name)
            signals15 = backtest.back_test(backtest_start,
                                           backtest_end)
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
    def calc_total_monthly_pnl(all_signals, new_signals):
        total_monthly_pnl = 0
        for s in new_signals:
            total_monthly_pnl = total_monthly_pnl + s.pnl
            all_signals.append(s)
        return total_monthly_pnl

    @staticmethod
    def get_historical_data(file):
        df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])
        return df

    @staticmethod
    def get_backtest(cb_chart, strategy, strategy_name):
        return CBBackTest(cb_chart, strategy)

    @staticmethod
    def get_hist_data_filename(index):
        file = './backtest/hist15min/' + index + '-HIST-15M.csv'
        return file

    def get_strategy(self, row, cb_chart, strategy_name):

        if strategy_name == 'STI':
            expiry = row['Expiry']
            stoploss_margin = int(row['StopLoss15'])
            return CBSuperTrendStrategy('SuperTrend15',
                                        cb_chart, expiry,
                                        stoploss_margin=stoploss_margin,
                                        supertrend_ma_margin=self.get_strategy_param_value('supertrend_ma_margin'),
                                        stoploss_gap=self.get_strategy_param_value('stoploss_gap'))

        if strategy_name == 'RSI-BUY':
            return RsiAdxBuyOrSellStrategy(
                cb_chart, float(row['StopLoss']), float(row['StopGain']), True, float(row['RSI']), float(row['ADXMin']),
                float(row['ADXMax']))

    def get_cbchart(self, df, symbol, lot_size, strategy_name):

        if strategy_name == 'STI':
            return CBChart(symbol, lot_size
                           , df, ema_interval=self.get_strategy_param_value('ema_interval'),
                           sma_interval=self.get_strategy_param_value('sma_interval'),
                           MA=self.get_strategy_param_value('MA'),
                           sti_interval=self.get_strategy_param_value('sti_interval'),
                           sti_multiplier=self.get_strategy_param_value('sti_multiplier'))

        if strategy_name == 'RSI-BUY':
            return CBChart(symbol, lot_size, df, ema_interval=self.get_strategy_param_value('ema_interval'))

    def get_strategy_param_value(self, strategy_param_key):
        return self.strategy_params_dict.get(strategy_param_key).get(0)

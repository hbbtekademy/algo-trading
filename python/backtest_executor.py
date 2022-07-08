import pandas as pd
from ChartBusters import constants
from ChartBusters.Strategy.cb_supertrend_backtest import CBSuperTrendBackTest

from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_signal import CBSignal
from ChartBusters.strategies.supertrend_strategy import CBSuperTrendStrategy


class BacktestExecutor:

    def __init__(self,driver_file,lot_size:int,symbol):
        self.driver_file=driver_file
        self.lot_size = lot_size
        self.symbol = symbol
        '''
        TODO: these constants are specific to each strategy but also needs to be passed to 
        the CBChart class which is agnostic to the strategy. Need to design this better.
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

    def execute(self,message) -> str:
        print('exec',message)
        all_signals = list()
        driver_file = self.get_driver_file()

        for index, row in driver_file.iterrows():
            file = self.get_hist_data_filename(index)
            df = self.get_historical_data(file)
            cb_chart = self.get_cbchart(df)
            strategy = self.get_strategy(row, cb_chart)
            backtest = self.get_backtest(row, cb_chart, strategy)
            signals15 = backtest.back_test(row['Start'].tz_localize('Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))
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

    def calc_total_pnl_and_count(self, all_signals):
        total_pnl = 0
        total_count = 0
        CBSignal.print_header()
        for signal in all_signals:
            total_pnl = total_pnl + signal.pnl
            total_count = total_count + 1
            signal.pretty_print()
        return total_pnl,total_count

    def calc_total_monthly_pnl(self, all_signals, signals15):
        total_monthly_pnl = 0
        for s in signals15:
            total_monthly_pnl = total_monthly_pnl + s.pnl
            all_signals.append(s)
        return total_monthly_pnl

    def get_historical_data(self, file):
        df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])
        return df

    def get_backtest(self, row, cb_chart,strategy):
        return CBSuperTrendBackTest(cb_chart,strategy)

    def get_hist_data_filename(self, index):
        file = './BackTest/Hist15min/' + index + '-HIST-15M.csv'
        return file

    def get_strategy(self, row, cb_chart):
        return CBSuperTrendStrategy('SuperTrend15',
                                    cb_chart, row['Expiry'],
                                    stoploss_margin=int(row['StopLoss15']),
                                    supertrend_ma_margin=self.supertrend_ma_margin, stoploss_gap=self.stoploss_gap)

    def get_cbchart(self, df):
        return CBChart(self.symbol,self.lot_size
        , df, ema_interval=self.ema_interval, sma_interval=self.sma_interval, MA=self.MA, sti_interval=self.sti_interval,
                    sti_multiplier=self.sti_multiplier)

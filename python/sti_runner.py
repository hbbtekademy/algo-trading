import pandas as pd
from ChartBusters.cb_chart import CBChart
from ChartBusters.Strategy.cb_supertrend_strategy import CBSuperTrendStrategy
from ChartBusters.Strategy.cb_supertrend_strategy_v1 import CBSuperTrendStrategyV1
from ChartBusters.Strategy.cb_supertrend_backtest import CBSuperTrendBackTest
from ChartBusters.cb_signal import CBSignal
from ChartBusters import helpers
from typing import List

from ChartBusters import constants

# file = './python/BackTest/config/STI_Nifty_BackTest_2021.csv'
# file = './python/BackTest/config/STI_Nifty_BackTest_2020.csv'
# file = './python/BackTest/config/STI_Nifty_BackTest_2019.csv'
# file = './python/BackTest/config/STI_Nifty_BackTest_2018.csv'
# file = './python/BackTest/config/STI_Nifty_BackTest_2017.csv'
file = './python/BackTest/config/STI_NiftyFut_Verify.csv'

# file = './python/BackTest/config/STI_BankNifty_BackTest_2021.csv'
# file = './python/BackTest/config/STI_BankNifty_BackTest_2020.csv'
# file = './python/BackTest/config/STI_BankNifty_BackTest_2019.csv'
# file = './python/BackTest/config/STI_BankNifty_BackTest_2018.csv'
# file = './python/BackTest/config/STI_BankNiftyFut_Verify.csv'

ema_interval = 31
sma_interval = 29
MA = constants.EMA
supertrend_ma_margin = 50
stoploss_gap = 20
sti_interval = 11
sti_multiplier = 2
# close_ema_margin = 2500000000

input_df = pd.read_csv(file, parse_dates=['Start', 'End'], index_col=['Sym'])

all_signals = list()
all_signals60 = list()
for index, row in input_df.iterrows():
    file = './python/BackTest/Hist15min/' + index + '-HIST-15M.csv'
    df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])

    chart = CBChart(index, int(
        row['LotSize']), df, ema_interval=ema_interval, sma_interval=sma_interval, MA=MA, sti_interval=sti_interval, sti_multiplier=sti_multiplier)

    strategy = CBSuperTrendStrategy('SuperTrend15',
                                    chart, row['Expiry'],
                                    stoploss_margin=int(row['StopLoss15']),
                                    supertrend_ma_margin=supertrend_ma_margin, stoploss_gap=stoploss_gap)

    backtest = CBSuperTrendBackTest(chart, strategy)

    # print(df.tail(50))

    signals15 = backtest.back_test(row['Start'].tz_localize(
        'Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))

    total_monthly_pnl = 0
    for s in signals15:
        total_monthly_pnl = total_monthly_pnl + s.pnl
        all_signals.append(s)

    print('{}'.format(total_monthly_pnl))

total_pnl = 0
total_count = 0
CBSignal.print_header()
for signal in all_signals:
    total_pnl = total_pnl + signal.pnl
    total_count = total_count + 1
    signal.pretty_print()

print(" ")
print(" ")
print("Total PnL,{},Total Trades,{}".format(total_pnl, total_count*2))

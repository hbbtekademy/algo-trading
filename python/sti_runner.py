import pandas as pd
from ChartBusters.cb_chart import CBChart
from ChartBusters.Strategy.cb_supertrend_strategy import CBSuperTrendStrategy
from ChartBusters.Strategy.cb_supertrend_strategy_v1 import CBSuperTrendStrategyV1
from ChartBusters.Strategy.cb_supertrend_backtest import CBSuperTrendBackTest
from ChartBusters.cb_signal import CBSignal
from ChartBusters import helpers
from typing import List

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

input_df = pd.read_csv(file, parse_dates=['Start', 'End'], index_col=['Sym'])

all_signals = list()
all_signals60 = list()
for index, row in input_df.iterrows():
    file = './python/BackTest/Hist15min/' + index + '-HIST-15M.csv'
    df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])
    df_60min = helpers.get_hourly_df(df)
    chart = CBChart(index, int(row['LotSize']), df, ema_interval=31)
    chart60 = CBChart(index, int(row['LotSize']), df_60min, ema_interval=31)

    backtest = CBSuperTrendBackTest(
        chart, chart60, row['Expiry'], stoploss_margin15=int(row['StopLoss15']), stoploss_margin60=int(row['StopLoss60']),
        close_margin=50)
    signals15, signals60 = backtest.back_test(row['Start'].tz_localize(
        'Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))

    total_monthly_pnl = 0
    for s in signals15:
        total_monthly_pnl = total_monthly_pnl + s.pnl
        all_signals.append(s)

    total_monthly_pnl60 = 0
    for s in signals60:
        total_monthly_pnl60 = total_monthly_pnl60 + s.pnl
        all_signals60.append(s)

    print('Monthly 15Min Pnl,{}'.format(total_monthly_pnl))
    # print('Monthly 60Min Pnl,{}'.format(total_monthly_pnl60))
    print(" ")

total_pnl = 0
total_count = 0
CBSignal.print_header()
for signal in all_signals:
    total_pnl = total_pnl + signal.pnl
    total_count = total_count + 1
    signal.pretty_print()

print(" ")
'''
print("Hourly Strategy results")
total_pnl60 = 0
total_count60 = 0
CBSignal.print_header()
for signal in all_signals60:
    total_pnl60 = total_pnl60 + signal.pnl
    total_count60 = total_count60 + 1
    signal.pretty_print()
'''


print(" ")
print("Total PnL,{},Total Count,{}".format(total_pnl, total_count))

# print(" ")
# print("Total PnL,{},Total Count,{}".format(total_pnl60, total_count60))

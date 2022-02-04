import pandas as pd
from ChartBusters.cb_chart import CBChart
from ChartBusters.Strategy.cb_supertrend_strategy import CBSuperTrendStrategy
from ChartBusters.Strategy.cb_supertrend_strategy_v1 import CBSuperTrendStrategyV1
from ChartBusters.Strategy.cb_supertrend_backtest import CBSuperTrendBackTest
from ChartBusters.cb_signal import CBSignal
from ChartBusters import helpers
from typing import List

# file = '/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/BackTest/temp.txt'
# file = '/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/BackTest/STI_Nifty_BackTest.csv'
file = '/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/BackTest/STI_BankNifty_BackTest.csv'
# file = '/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/BackTest/STI_NiftyFut_Verify.csv'

input_df = pd.read_csv(file, parse_dates=['Start', 'End'], index_col=['Sym'])

all_signals = list()
all_signals60 = list()
for index, row in input_df.iterrows():
    file = '/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/BackTest/Hist15min/' + \
        index + '-HIST-15M.csv'
    df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])
    df_60min = helpers.get_hourly_df(df)
    chart = CBChart(index, int(row['LotSize']), df, ema_interval=31)
    chart60 = CBChart(index, int(row['LotSize']), df_60min, ema_interval=31)

    backtest = CBSuperTrendBackTest(
        chart, chart60, row['Expiry'], stoploss_margin15=180, stoploss_margin60=200)
    signals15, signals60 = backtest.back_test(row['Start'].tz_localize(
        'Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))

    total_monthly_pnl = 0
    for signal in signals15:
        total_monthly_pnl = total_monthly_pnl + signal.pnl
        all_signals.append(signal)

    total_monthly_pnl60 = 0
    for signal in signals60:
        total_monthly_pnl60 = total_monthly_pnl60 + signal.pnl
        all_signals60.append(signal)

    print('Monthly 15Min Pnl,{}'.format(total_monthly_pnl))
    print('Monthly 60Min Pnl,{}'.format(total_monthly_pnl60))
    print(" ")
    '''strategy = CBSuperTrendStrategy(chart, row['Expiry'])
    results = strategy.back_test(row['Start'].tz_localize(
        'Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))

    for result in results:
        all_signals.append(result)

    strategy60 = CBSuperTrendStrategy(chart60, row['Expiry'])
    results = strategy60.back_test(row['Start'].tz_localize(
        'Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))

    for result in results:
        all_signals60.append(result)'''

total_pnl = 0
CBSignal.print_header()
for signal in all_signals:
    total_pnl = total_pnl + signal.pnl
    signal.pretty_print()

print(" ")
print("Hourly Strategy results")
total_pnl60 = 0
CBSignal.print_header()
for signal in all_signals60:
    total_pnl60 = total_pnl60 + signal.pnl
    signal.pretty_print()


print(" ")
print("Total PnL,{}".format(total_pnl))

print(" ")
print("Total PnL,{}".format(total_pnl60))

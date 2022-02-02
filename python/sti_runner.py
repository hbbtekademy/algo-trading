import pandas as pd
from ChartBusters.cb_chart import CBChart
from ChartBusters.Strategy.cb_supertrend_strategy import CBSuperTrendStrategy

file = '/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/BackTest/temp.txt'

input_df = pd.read_csv(file, parse_dates=['Start', 'End'], index_col=['Sym'])

all_signals = list()
for index, row in input_df.iterrows():
    file = '/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/BackTest/Hist15min/' + \
        index + '-HIST-15M.csv'
    df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])

    chart = CBChart(index, int(row['LotSize']), df, ema_interval=31)
    strategy = CBSuperTrendStrategy(chart, 2500, 13000, row['Expiry'])
    results = strategy.back_test(row['Start'].tz_localize(
        'Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))

    for result in results:
        all_signals.append(result)
        print(result)

total_pnl = 0
for signal in all_signals:
    total_pnl = total_pnl + signal.pnl

print(" ")
print("Total PnL: {}".format(total_pnl))

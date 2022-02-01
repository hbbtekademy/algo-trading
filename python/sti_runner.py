import pandas as pd
from ChartBusters.cb_chart import CBChart
from ChartBusters.Strategy.cb_supertrend_strategy import CBSuperTrendStrategy

file = '/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/BackTest/Hist15min/NIFTY22FEBFUT-HIST-15M.csv'
sym = 'NIFTY22JANFUT'
lot_size = 100

df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])

chart = CBChart(sym, lot_size, df, ema_interval=31)

strategy = CBSuperTrendStrategy(chart, 6000, 13000)
results = strategy.back_test('2022-01-26', '2022-02-01')

total_pnl = 0
for result in results:
    total_pnl = total_pnl + result.pnl
    print(result)

print(" ")
print("Total PnL: {}".format(total_pnl))

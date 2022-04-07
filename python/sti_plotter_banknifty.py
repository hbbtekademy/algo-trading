import pandas as pd
from ChartBusters.cb_chart import CBChart
from ChartBusters.Plot.cb_supertrend_plot import CBSuperTrendPlot
from ChartBusters import helpers
from ChartBusters import constants

file = './python/BackTest/Hist15min/BANKNIFTY-HIST-15M.csv'
sym = 'BANKNIFTY'
lot_size = 50
MA = constants.SMA
sma_interval = 31
sti_interval = 11
sti_multiplier = 1
macd_fast = 19
macd_slow = 41
macd_sign = 11


df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])
df_30min = helpers.get_30min_df(df)

chart = CBChart(sym, lot_size, df_30min, MA=MA, sma_interval=sma_interval,
                sti_interval=sti_interval, sti_multiplier=sti_multiplier,
                macd_fast=macd_fast, macd_slow=macd_slow, macd_sign=macd_sign)

sti_plot = CBSuperTrendPlot(chart)

sti_plot.plot('2021-03-01', '2021-03-31')

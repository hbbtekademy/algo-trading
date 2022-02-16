import pandas as pd
import pandas_ta as ta
from ChartBusters import helpers
from ChartBusters.cb_chart import CBChart
from ChartBusters.Plot.cb_supertrend_plot import CBSuperTrendPlot

file = './python/BackTest/Hist15min/NIFTY22FEBFUT-HIST-15M.csv'
# file = './python/BackTest/Hist15min/NIFTY-HIST-15M.csv'
sym = 'NIFTY'
lot_size = 75
df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])

chart15 = CBChart(sym, lot_size, df, ema_interval=31, sma_interval=29, sti_interval=11, sti_multiplier=2)

sti_plot = CBSuperTrendPlot(chart15)

sti_plot.plot('2022-02-15', '2022-02-17')

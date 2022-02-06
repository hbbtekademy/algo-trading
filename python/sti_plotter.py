import pandas as pd
import pandas_ta as ta
from ChartBusters import helpers
from ChartBusters.cb_chart import CBChart
from ChartBusters.Plot.cb_supertrend_plot import CBSuperTrendPlot

file = './python/BackTest/Hist15min/NIFTY22JANFUT-HIST-15M.csv'
sym = 'NIFTY22JANFUT'
lot_size = 50
df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])

chart15 = CBChart(sym, lot_size, df, ema_interval=31)

sti_plot = CBSuperTrendPlot(chart15)

sti_plot.plot('2021-12-21', '2021-12-31')

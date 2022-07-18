import pandas as pd

from chartbusters.plot.cb_supertrend_plot import CBSuperTrendPlot
from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.util import constants, helpers

file = 'backtest/hist15min/BANKNIFTY-HIST-15M.csv'
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
df_30min = helpers.get_revised_interval_df(df, '60Min', '15Min')

chart = CBChart(sym, lot_size, df_30min, MA=MA, sma_interval=sma_interval,
                sti_interval=sti_interval, sti_multiplier=sti_multiplier,
                macd_fast=macd_fast, macd_slow=macd_slow, macd_sign=macd_sign)

sti_plot = CBSuperTrendPlot(chart)

sti_plot.plot('2021-03-01', '2021-03-31')

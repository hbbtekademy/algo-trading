import pandas as pd

from chartbusters.plot.cb_supertrend_plot import CBSuperTrendPlot
from python.chartbusters.model.cb_chart import CBChart

# file = './python/backtest/hist15min/NIFTY22FEBFUT-HIST-15M.csv'
# file = './python/backtest/hist15min/NIFTY22MARFUT-HIST-15M.csv'
file = './python/backtest/hist15min/NIFTY22APRFUT-HIST-15M.csv'
# file = './python/backtest/hist15min/NIFTY-HIST-15M.csv'
sym = 'NIFTY'
lot_size = 50
df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])

chart15 = CBChart(sym, lot_size, df, ema_interval=31,
                  sma_interval=29, sti_interval=11, sti_multiplier=2)

sti_plot = CBSuperTrendPlot(chart15)

sti_plot.plot('2022-03-25', '2022-04-15')

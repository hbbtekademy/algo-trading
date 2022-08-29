import pandas as pd

from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.strategies.supertrend.basic.cb_supertrend_strategy_v3 import CBSuperTrendStrategyV3
# file = './python/backtest/config/STI_Nifty_BackTest_2021.csv'
# file = './python/backtest/config/STI_Nifty_BackTest_2020.csv'
# file = './python/backtest/config/STI_Nifty_BackTest_2019.csv'
# file = './python/backtest/config/STI_Nifty_BackTest_2018.csv'
# file = './python/backtest/config/STI_Nifty_BackTest_2017.csv'
from python.chartbusters.util import helpers

file = 'backtest/config/driver_files/STI_NiftyFut_Verify.csv'

# file = './python/backtest/config/STI_BankNifty_BackTest_2021.csv'
# file = './python/backtest/config/STI_BankNifty_BackTest_2020.csv'
# file = './python/backtest/config/STI_BankNifty_BackTest_2019.csv'
# file = './python/backtest/config/STI_BankNifty_BackTest_2018.csv'
# file = './python/backtest/config/STI_BankNiftyFut_Verify.csv'

ema_interval = 31
supertrend_ema_margin = 30
stoploss_gap = 20
close_ema_margin = 35000000

input_df = pd.read_csv(file, parse_dates=['Start', 'End'], index_col=['Sym'])

all_signals = list()
for index, row in input_df.iterrows():
    file = './backtest/hist15min/' + index + '-HIST-15M.csv'
    df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])
    print(df)
    df_60min = helpers.get_revised_interval_df(df, '60Min', '15Min')
    chart = CBChart(index, int(row['LotSize']), df, ema_interval=ema_interval)

    strategy = CBSuperTrendStrategyV3(
        index, chart, row['Expiry'], stoploss_margin=int(row['StopLoss15']), stoploss_gap=stoploss_gap,
        supertrend_ema_margin=supertrend_ema_margin, close_ema_margin=close_ema_margin)

    strategy.back_test(row['Start'].tz_localize('Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))

import pandas as pd

from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v1 import CBSignalV1
from python.chartbusters.strategies.cb_backtest import CBBackTest
from python.chartbusters.strategies.supertrend.basic.cb_supertrend_strategy import CBSuperTrendStrategy
from python.chartbusters.util import constants

# file = './python/backtest/config/STI_Nifty_BackTest_2021.csv'
# file = './python/backtest/config/STI_Nifty_BackTest_2020.csv'
# file = './python/backtest/config/STI_Nifty_BackTest_2019.csv'
# file = './python/backtest/config/STI_Nifty_BackTest_2018.csv'
# file = './python/backtest/config/STI_Nifty_BackTest_2017.csv'
file = 'backtest/config/driver_files/STI_NiftyFut_Verify.csv'

# file = './python/backtest/config/STI_BankNifty_BackTest_2021.csv'
# file = './python/backtest/config/STI_BankNifty_BackTest_2020.csv'
# file = './python/backtest/config/STI_BankNifty_BackTest_2019.csv'
# file = './python/backtest/config/STI_BankNifty_BackTest_2018.csv'
# file = './python/backtest/config/STI_BankNiftyFut_Verify.csv'

ema_interval = 31
sma_interval = 29
MA = constants.EMA
supertrend_ma_margin = 50
stoploss_gap = 20
sti_interval = 11
sti_multiplier = 2
# close_ema_margin = 2500000000

input_df = pd.read_csv(file, parse_dates=['Start', 'End'], index_col=['Sym'])

all_signals = list()
all_signals60 = list()
for index, row in input_df.iterrows():
    file = './backtest/hist15min/' + index + '-HIST-15M.csv'
    print('Historical data file:',file)
    df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])

    chart = CBChart(index, int(
        row['LotSize']), df, ema_interval=ema_interval, sma_interval=sma_interval, MA=MA, sti_interval=sti_interval,
                    sti_multiplier=sti_multiplier)

    strategy = CBSuperTrendStrategy('SuperTrend15',
                                    chart, row['Expiry'],
                                    stoploss_margin=int(row['StopLoss15']),
                                    supertrend_ma_margin=supertrend_ma_margin, stoploss_gap=stoploss_gap)

    backtest = CBBackTest(chart, strategy)

    # print(df.tail(50))

    signals15 = backtest.back_test(row['Start'].tz_localize(
        'Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))

    total_monthly_pnl = 0
    for s in signals15:
        total_monthly_pnl = total_monthly_pnl + s.pnl
        all_signals.append(s)

    print('{}'.format(total_monthly_pnl))

total_pnl = 0
total_count = 0
CBSignalV1.print_header()
for signal in all_signals:
    total_pnl = total_pnl + signal.pnl
    total_count = total_count + 1
    signal.pretty_print()

print(" ")
print(" ")
print("Total PnL,{},Total Trades,{}".format(total_pnl, total_count * 2))

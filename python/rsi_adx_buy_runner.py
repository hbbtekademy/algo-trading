import pandas as pd

from chartbusters.cb_chart import CBChart
from chartbusters.cb_signal import CBSignal
from chartbusters.strategy.buy.cb_rsi_adx_buy_strategy import RsiAdxBuyStrategy
from chartbusters.strategy.cb_backtest_result import CBBackTestResult

file = './python/backtest/config/RSI_ADX_Buy_Verify_Feb.csv'

input_df = pd.read_csv(file, parse_dates=['Start', 'End'], index_col=['Sym'])

CBBackTestResult.print_header()
all_signals = list()
for index, row in input_df.iterrows():
    file = './python/backtest/hist15min/' + \
           index + '-HIST-15M.csv'
    df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])

    chart = CBChart(index, int(row['LotSize']), df, ema_interval=10)

    strategy = RsiAdxBuyStrategy(
        chart, float(row['StopLoss']), float(row['StopGain']), float(row['RSI']), float(row['ADXMin']),
        float(row['ADXMax']))

    btResult = strategy.back_test(row['Start'].tz_localize(
        'Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))
    btResult.pretty_print()
    for signal in btResult.signals:
        all_signals.append(signal)

print(" ")
CBSignal.print_header()
total_pnl = 0
for signal in all_signals:
    signal.pretty_print()
    total_pnl = total_pnl + signal.pnl

print('Total PnL: {}'.format(total_pnl))

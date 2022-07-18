import pandas as pd

from chartbusters.strategies.cb_backtest_result import CBBackTestResult
from chartbusters.strategies.rsi.cb_rsi_adx_buy_or_sell_strategy import RsiAdxBuyOrSellStrategy
from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v1 import CBSignalV1

file = './backtest/config/RSI_ADX_Buy_BackTest.csv'

input_df = pd.read_csv(file, parse_dates=['Start', 'End'], index_col=['Sym'])

CBBackTestResult.print_header()
all_signals = list()
for index, row in input_df.iterrows():
    file = './backtest/hist15min/' + \
           index + '-HIST-15M.csv'
    df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])

    chart = CBChart(index, int(row['LotSize']), df, ema_interval=10)

    strategy = RsiAdxBuyOrSellStrategy(
        chart, float(row['StopLoss']), float(row['StopGain']), True, float(row['RSI']), float(row['ADXMin']),
        float(row['ADXMax']))

    btResult = strategy.back_test(row['Start'].tz_localize(
        'Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))
    btResult.pretty_print()
    for signal in btResult.signals:
        all_signals.append(signal)

print(" ")
CBSignalV1.print_header()
total_pnl = 0
for signal in all_signals:
    signal.pretty_print()
    total_pnl = total_pnl + signal.pnl

print('Total PnL: {}'.format(total_pnl))

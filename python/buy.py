import pandas as pd
import pandas_ta as ta
from ChartBusters import constants
from ChartBusters.cb_candle import CBCandle
from ChartBusters.cb_chart import CBChart
from ChartBusters.Strategy.Buy.cb_rsi_adx_buy_strategy import RSI_ADX_Buy_Strategy
from ChartBusters.Strategy.Sell.cb_rsi_adx_sell_strategy import RSI_ADX_Sell_Strategy
from ChartBusters.Strategy.cb_backtest_result import CBBackTestResult
from ChartBusters.cb_signal import CBSignal

file = '/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/BackTest/temp.txt'

input_df = pd.read_csv(file, parse_dates=['Start', 'End'], index_col=['Sym'])

CBBackTestResult.print_header()
all_signals = list()
for index, row in input_df.iterrows():
    file = '/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/BackTest/Hist15min/' + \
        index + '-HIST-15M.csv'
    df = pd.read_csv(file, parse_dates=['Date'], index_col=['Date'])

    chart = CBChart(index, int(row['LotSize']), df)

    strategy = RSI_ADX_Buy_Strategy(
        chart, float(row['StopLoss']), float(row['StopGain']), float(row['RSI']), float(row['ADXMin']), float(row['ADXMax']))

    btResult = strategy.back_test(row['Start'].tz_localize(
        'Asia/Kolkata'), row['End'].tz_localize('Asia/Kolkata'))
    btResult.pretty_print()
    for signal in btResult.signals:
        all_signals.append(signal)

print(" ")
CBSignal.print_header()
for signal in all_signals:
    signal.pretty_print()

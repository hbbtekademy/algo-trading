import sys
from os.path import exists

import numpy as np
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import ADXIndicator
from ta.trend import MACD

import helpers
from backtest_result import BackTestResult
from signal import Signal

# print(sys.argv[0], sys.argv[1], sys.argv[2])

file_15min = sys.argv[1]

file_exists = exists(file_15min)
if (file_exists != True):
    exit(0)

# strategies params
strategy = 'RSIBuy'
sym = sys.argv[2]
window_start = '2021-01-01 00:00:00'
window_end = '2022-01-01 00:00:00'
rsi_15min = 70
rsi_60min = 50
lot_size = int(sys.argv[3])
stop_loss = 6500
stop_gain = 13000
back_candles = 5
adx_low = 30
adx_high = 40
volume_multiple = 2  # 2 or 3 times
daily_movement_pct = 4
check_volume = True
rsi_60min_check = False
macd_check = False

print("Running RSI rsi strategies for {}".format(sym))

df_15min = pd.read_csv(file_15min, parse_dates=['Date'], index_col=['Date'])

# Add RSI
rsi = RSIIndicator(df_15min['Close']).rsi()
df_15min = df_15min.assign(rsi=rsi.values)

# Add Vol SMA 5
vol_sma5 = df_15min['Volume'].rolling(5).mean()
df_15min = df_15min.assign(vol_sma5=vol_sma5.values)

# Add ADX
ADX = ADXIndicator(high=df_15min['High'],
                   low=df_15min['Low'], close=df_15min['Close'])
df_15min = df_15min.assign(adx=ADX.adx().values)
df_15min = df_15min.assign(adx_neg=ADX.adx_neg().values)
df_15min = df_15min.assign(adx_pos=ADX.adx_pos().values)

# Add MACD
MACD = MACD(df_15min['Close'])
df_15min = df_15min.assign(macd=MACD.macd().values)
df_15min = df_15min.assign(macd_sig=MACD.macd_signal().values)
df_15min = df_15min.assign(macd_diff=MACD.macd_diff().values)
# print(df_15min.tail())

# Get candles that close above 70 RSI
curr_window_df = df_15min[window_start:window_end]

rsi_filter = (curr_window_df['rsi'] > rsi_15min)
df = curr_window_df[rsi_filter]

bullish_filter = (df['Close'] > df['Open'])
df = df[bullish_filter]

temp_df = pd.DataFrame(columns=df_15min.columns)
temp_df.index.name = 'Date'
back_candles_df = pd.DataFrame()

for index, row in df.iterrows():
    back_candles_df = helpers.get_previous_candles(curr_window_df, index, 1)
    prev_rsi = 0
    if (back_candles_df.shape[0] != 0):
        prev_rsi = back_candles_df.iloc[0]['rsi']

    if (prev_rsi < rsi_15min):
        temp_df.loc[index] = row

df = temp_df[df_15min.columns]
# print(df.head())

# Volume check
if (check_volume == True):
    temp_df = pd.DataFrame(columns=df_15min.columns)
    temp_df.index.name = 'Date'

    for index, row in df.iterrows():
        # Compare volume against previous mean volume
        if(row['Volume'] > volume_multiple*row['vol_sma5']):
            # print('Current Volume:', row['Volume'], 'greather than 2 times mean volume', mean_volume)
            temp_df.loc[index] = row

    df = temp_df[df_15min.columns]
    # print(df.head())

# Hourly RSI check
if (rsi_60min_check == True):
    temp_df = pd.DataFrame(columns=df.columns)
    temp_df.index.name = 'Date'

    for index, row in df.iterrows():
        df_60min = helpers.get_hourly_df(df_15min, index)
        # print(df_60min.tail(15))

        rsi = df_60min.iloc[-1]['rsi']
        if(rsi > rsi_60min):
            # This 15min candle is eligible for signal
            # print('Hourly candle RSI is greater than 50..', rsi)
            temp_df.loc[index] = row

    df = temp_df
    # print(df.head())

# Stock movement check
temp_df = pd.DataFrame(columns=df.columns)
temp_df.index.name = 'Date'

for index, row in df.iterrows():
    tanaji_pct = helpers.get_tanaji_pct(df_15min, index, 5, row['High'])
    # print('tanaji_pct:', tanaji_pct)
    if(tanaji_pct < daily_movement_pct):
        temp_df.loc[index] = row

df = temp_df
# print(df.head())

# Stop Loss check
temp_df = pd.DataFrame(columns=df.columns)
temp_df.index.name = 'Date'

for index, row in df.iterrows():
    prev_candle = helpers.get_previous_candles(df_15min, index, 1)
    prev_low = prev_candle.iloc[0]['Low']
    if((row['High'] - prev_low)*lot_size > stop_loss):
        # print(index, 'Stop Loss greater than 6000 INR. Do not trade', (row['High'] - prev_low)*lot_size)
        continue
    else:
        # print(index, 'Stop Loss within range', (row['High'] - prev_low)*lot_size)
        temp_df.loc[index] = row

df = temp_df
# print(df)

# ADX Check
temp_df = pd.DataFrame(columns=df.columns)
temp_df.index.name = 'Date'

for index, row in df.iterrows():
    if (row['adx'] >= adx_low and row['adx'] <= adx_high):
        print(type(df), type(row), type(df['Open']))
        # print(df)
        print(type(row.name))
        temp_df.loc[index] = row

df = temp_df

# MACD Check
if(macd_check == True):
    temp_df = pd.DataFrame(columns=df.columns)
    temp_df.index.name = 'Date'
    macd_diff = row['macd_diff']

    back_candles_df = helpers.get_previous_candles(curr_window_df, index, 1)
    prev_macd_diff = back_candles_df.iloc[0]['macd_diff']

    for index, row in df.iterrows():
        if (macd_diff > 0 and prev_macd_diff < 0):
            temp_df.loc[index] = row

    df = temp_df

# Final signal
signals = list()
for index, row in df.iterrows():
    stop_loss_candle = helpers.get_previous_candles(df_15min, index, 1)
    sig_stop_loss = stop_loss_candle.iloc[0]['Low']
    sig_entry = row['High']
    sig_daily_mov_pct = np.round(helpers.get_tanaji_pct(
        df_15min, index, 5, row['High']), 2)
    sig_rsi = np.round(row['rsi'], 2)
    sig_hourly_rsi = np.round(helpers.get_hourly_df(
        df_15min, index).iloc[-1]['rsi'], 2)
    sig_mean_volume = row['vol_sma5']
    sig_volume = row['Volume']
    signal = Signal(strategy=strategy, sym=sym, lot_size=lot_size,
                    ts=index, entry_price=sig_entry, stop_loss=sig_stop_loss,
                    rsi=sig_rsi, hourly_rsi=sig_hourly_rsi, vol=sig_volume,
                    mean_vol=sig_mean_volume, daily_mov_pct=sig_daily_mov_pct)
    signals.append(signal)

for signal in signals:
    helpers.generate_buy_signal_pnl(signal, df_15min, stop_gain=stop_gain)

btResult = BackTestResult(sym=sym, signals=signals)

for signal in btResult.signals:
    print(signal)

print(btResult)

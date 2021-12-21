from ta.momentum import RSIIndicator
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def get_previous_candles(df, index, n):
    loc = df.index.get_loc(index)
    return df.iloc[loc-1-n:loc-1]


def get_next_candles(df, index, n):
    loc = df.index.get_loc(index)
    return df.iloc[loc+1:loc+1+index]


def get_candlestick_plot(df):
    return go.Candlestick(x=df['DateStr'],
                          open=df['Open'],
                          high=df['High'],
                          low=df['Low'],
                          close=df['Close'],
                          increasing_line_color='yellow',
                          increasing_fillcolor='yellow',
                          decreasing_line_color='red',
                          decreasing_fillcolor='red',
                          )


def get_scatter_plot(df):
    return go.Scatter(
        x=df['DateStr'], y=df['rsi'])


ohlc_dict = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
}

volume_dict = {
    'Volume': 'sum'
}

df_15min = pd.read_csv('/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/RSITest/BHARTIARTL21DECFUT-HIST-15M.csv',
                       parse_dates=['Date'], index_col=['Date'])

rsi = RSIIndicator(df_15min['Close']).rsi()
df_15min = df_15min.assign(rsi=rsi.values)
print(df_15min.tail(15))

df_60min_ohlc = df_15min['Close'].resample('60Min', offset='30Min').apply(ohlc_dict)
# print(df_60min_ohlc.head(15))

df_60min_o = df_15min['Open'].resample('60Min', offset='30Min').apply({'Open':'first'})
df_60min_h = df_15min['High'].resample('60Min', offset='30Min').apply({'Open': 'max'})
df_60min_l = df_15min['Low'].resample('60Min', offset='30Min').apply({'Low': 'min'})
df_60min_c = df_15min['Close'].resample('60Min', offset='30Min').apply({'Close': 'last'})
df_60min_vol = df_15min['Volume'].resample('60Min', offset='30Min').apply({'Volume': 'sum'})
df_60min = pd.concat([df_60min_o, df_60min_h, df_60min_l,
                     df_60min_c, df_60min_vol], axis=1)

#print(df_60min.head(15))

#print(df_60min_vol.head(15))
df_60min.dropna(subset=['Open'], inplace=True)
#print(df_60min.tail(15))

rsi = RSIIndicator(df_60min['Close']).rsi()
df_60min = df_60min.assign(rsi=rsi.values)
print(df_60min.tail(15))

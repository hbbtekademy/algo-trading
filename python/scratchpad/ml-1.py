import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py
from plotly.subplots import make_subplots
from ta.momentum import RSIIndicator
from ta.volume import ChaikinMoneyFlowIndicator
from ta.trend import MACD

print("pandas version:",pd.__version__)
print("numpy version:",np.__version__)


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


file_15min = '/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/Nifty100Hist15min/RELIANCE-HIST.csv'
df_15min = pd.read_csv(file_15min, parse_dates=['Date'], index_col=['Date'])

rsi = RSIIndicator(df_15min['Close']).rsi()
df_15min = df_15min.assign(rsi=rsi.values)

cmf = ChaikinMoneyFlowIndicator(
    df_15min['High'], df_15min['Low'], df_15min['Close'], df_15min['Volume']).chaikin_money_flow()
df_15min = df_15min.assign(cmf=cmf.values)

macd = MACD(df_15min['Close'])
df_15min = df_15min.assign(macd=macd.macd().values)
df_15min = df_15min.assign(macd_sig=macd.macd_signal().values)

print(type(rsi), type(cmf), type(macd))

df_15min.dropna(inplace=True)

df_15min['DateStr'] = df_15min.index.strftime('%d-%m %H:%M')

df_15min.head()

fig = make_subplots(rows=1, cols=1, shared_xaxes=False,
                    vertical_spacing=0.1,
                    subplot_titles=('Stock'))


fig.add_trace(get_candlestick_plot(df_15min),
              row=1, col=1)

fig.update_xaxes(type='category', rangeslider=dict(visible=True))
fig.update_xaxes(showgrid=False, nticks=10)
fig.update_yaxes(showgrid=False)
fig.show()

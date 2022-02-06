from ta.momentum import RSIIndicator
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def get_scatter_plot(df, marker_color='blue', name='rsi'):
    return go.Scatter(
        x=df['DateStr'], y=df['rsi'], marker_color=marker_color, name=name)


df_15min = pd.read_csv('/Users/hbb/MyDocs/Work/Startup/AlgoTrading/TickData/Nifty100Hist15min/BOSCHLTD-HIST.csv',
                       parse_dates=['Date'], index_col=['Date'])

df_15min['DateStr'] = df_15min.index.strftime('%d-%m %H:%M')

rsi = RSIIndicator(df_15min['Close']).rsi()
df_rsi_full_15min = df_15min.assign(rsi=rsi.values)
print(df_15min)
print('Full df')
print(df_rsi_full_15min)

rsi = RSIIndicator(df_15min[-16:]['Close']).rsi()
df_rsi_back16_15min = df_15min[-16:].assign(rsi=rsi.values)
print('Last 16 df')
print(df_rsi_back16_15min)

rsi = RSIIndicator(df_15min[-45:]['Close']).rsi()
df_rsi_back45_15min = df_15min[-45:].assign(rsi=rsi.values)
print('Last 45 df')
print(df_rsi_back45_15min)

rsi = RSIIndicator(df_15min[-60:]['Close']).rsi()
df_rsi_back60_15min = df_15min[-60:].assign(rsi=rsi.values)

rsi = RSIIndicator(df_15min[-120:]['Close']).rsi()
df_rsi_back120_15min = df_15min[-120:].assign(rsi=rsi.values)

rsi = RSIIndicator(df_15min[-180:]['Close']).rsi()
df_rsi_back180_15min = df_15min[-180:].assign(rsi=rsi.values)

fig = make_subplots(rows=1, cols=1, shared_xaxes=False,
                    vertical_spacing=0.1, horizontal_spacing=0.01,
                    subplot_titles=('RSI'),
                    row_width=[1])

back = -30
fig.add_trace(get_scatter_plot(df_rsi_full_15min[back:], marker_color='Blue', name='rsi full'),
              row=1, col=1)
fig.add_trace(get_scatter_plot(df_rsi_back45_15min[back:], marker_color='Red', name='rsi 45'),
              row=1, col=1)
fig.add_trace(get_scatter_plot(df_rsi_back60_15min[back:], marker_color='Orange', name='rsi 60'),
              row=1, col=1)
fig.add_trace(get_scatter_plot(df_rsi_back120_15min[back:], marker_color='Cyan', name='rsi 120'),
              row=1, col=1)
fig.add_trace(get_scatter_plot(df_rsi_back180_15min[back:], marker_color='Yellow', name='rsi 180'),
              row=1, col=1)

fig.update_xaxes(type='category', rangeslider=dict(visible=False))
fig.update_xaxes(showgrid=False, nticks=5)
fig.update_yaxes(showgrid=False)

fig.update_layout(
    title='RSI Comparison for different intervals',
    plot_bgcolor='rgb(5,5,5)',
    paper_bgcolor='rgb(0,0,0)',
    font_color='white')

fig.show()

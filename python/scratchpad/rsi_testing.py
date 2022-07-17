import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ta.momentum import RSIIndicator


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


df_15min = pd.read_csv(
    '..//TickData/Nifty100Hist15min/ACC-HIST.csv', parse_dates=['Date'], index_col=['Date'])

df_60min = pd.read_csv(
    '../TickData/Nifty100Hist60min/ACC-HIST-60M.csv', parse_dates=['Date'], index_col=['Date'])

df_15min = df_15min['2020-11-01 00:00:00':'2021-12-16 00:00:00']
df_60min = df_60min['2020-11-01 00:00:00':'2021-12-16 00:00:00']

rsi = RSIIndicator(df_15min['Close']).rsi()
df_15min = df_15min.assign(rsi=rsi.values)

rsi = RSIIndicator(df_60min['Close']).rsi()
df_60min = df_60min.assign(rsi=rsi.values)

df_15min['DateStr'] = df_15min.index.strftime('%d-%m %H:%M')
df_60min['DateStr'] = df_60min.index.strftime('%d-%m %H:%M')

# print(df_15min.head(15))
# print(df_60min.head(15))

ohlc_dict = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum',
}

df_mod_60min = get_previous_candles(df_15min, '2021-12-03 14:30:00', 400).resample(
    '60Min', offset='15min').apply(ohlc_dict)
df_mod_60min.dropna(inplace=True)
rsi = RSIIndicator(df_mod_60min['Close']).rsi()
df_mod_60min = df_mod_60min.assign(rsi=rsi.values)

df_mod_60min['DateStr'] = df_mod_60min.index.strftime('%d-%m %H:%M')

print('60min rsi:' + str(df_60min.loc['2021-12-03 11:15:00']['rsi']))
print('60min rsi:' + str(df_mod_60min.loc['2021-12-03 11:15:00']['rsi']))

fig = make_subplots(rows=4, cols=1, shared_xaxes=False,
                    vertical_spacing=0.1, horizontal_spacing=0.01,
                    subplot_titles=(
                        'OHLC 15min', 'RSI 15min', 'OHLC 60min', 'RSI 60min'),
                    # column_widths=[0.75, 0.25],
                    # row_heights=[0.75, 0.25],
                    row_width=[0.3, 0.7, 0.3, 0.7])

fig.add_trace(get_candlestick_plot(df_15min['01-Dec-2021':'07-Dec-2021']),
              row=1, col=1)

fig.add_trace(get_scatter_plot(df_15min['01-Dec-2021':'07-Dec-2021']),
              row=2, col=1)

fig.add_trace(get_candlestick_plot(df_60min['01-Dec-2021':'07-Dec-2021']),
              row=3, col=1)

fig.add_trace(get_scatter_plot(df_60min['01-Dec-2021':'07-Dec-2021']),
              row=4, col=1)

fig.update_xaxes(type='category', rangeslider=dict(visible=False))
fig.update_xaxes(showgrid=False, nticks=10)
fig.update_yaxes(showgrid=False)
fig.update_yaxes(visible=False, row=1, col=2)
fig.update_xaxes(visible=False, row=1, col=2)
fig.update_layout(
    title='Signal generated for RSI 15mins strategy',
    title_x=0.5,
    plot_bgcolor='rgb(15,15,15)',
    paper_bgcolor='rgb(0,0,0)',
    font_color='white')

# fig.show()

import plotly.graph_objects as go

import pandas as pd
from datetime import datetime

df = pd.read_csv(
    '/Users/hbb/MyDocs/Work/Startup/KiteAPI/TickData/20211217/stick-738561-20211217.csv')

fig = go.Figure(data=[go.Candlestick(x=df['ExcTS'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])

fig.show()

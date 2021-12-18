import plotly.graph_objects as go
import pandas as pd
import os
import glob

from datetime import datetime
from pathlib import Path


candlestick_duration = '15Min'
base_dir = "../TickData/20211217"

for filename in glob.glob(base_dir + '/candlesticks/*.csv'):
    print("Processing file: "+filename)
    if os.path.isfile(filename):
        df = pd.read_csv(filename)
        stem = Path(filename).stem
        fig = go.Figure(data=[go.Candlestick(x=df['ExcTS'],
                                             open=df['open'],
                                             high=df['high'],
                                             low=df['low'],
                                             close=df['close'])])

        fig.write_html(base_dir + '/html/' + stem + '.html')

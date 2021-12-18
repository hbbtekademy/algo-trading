import pandas as pd
import os
import glob
from pathlib import Path

from pandas.core.indexes import base


def convert_ticks_to_candlestick(tick_file, duration):
    df = pd.read_csv(
        tick_file,
        parse_dates=['ExcTS', 'LastTradeTS'],
        index_col=['ExcTS']
    )

    candlestickDF = df['LastPrice'].resample(duration).ohlc()
    return candlestickDF


def write_candlesticks_to_file(candlestick_file, candlestickDF):
    candlestickDF.to_csv(candlestick_file)


def market_hours_filter(df):
    start_time = '2021-12-17 09:00:00'
    end_time = '2021-12-17 16:00:00'
    return df.loc[start_time:end_time]


candlestick_duration = '15Min'
base_dir = "../TickData/20211217"

for filename in glob.glob(base_dir + "/*.csv"):
    print("Processing file: "+filename)
    stem = Path(filename).stem
    if os.path.isfile(filename):
        candlestickDF = convert_ticks_to_candlestick(
            filename, candlestick_duration)

        candlestickDF = market_hours_filter(candlestickDF)
        write_candlesticks_to_file(
            base_dir + '/candlesticks/' + stem + '-' + candlestick_duration + '.csv', candlestickDF)

print('Done!')

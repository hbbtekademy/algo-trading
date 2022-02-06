import pandas as pd
from ta.momentum import RSIIndicator

df = pd.read_csv('../TickData/Nifty100Hist15min/ACC-HIST.csv',
                 parse_dates=['Date'], index_col=['Date'])

rsi = RSIIndicator(df['Close']).rsi()

df = df.assign(rsi=rsi.values)

currentMonthDF = df['2021-12-01 00:00:00':'2021-12-18 00:00:00']

above70RSI = currentMonthDF[currentMonthDF['rsi'] > 70]

for index, row in above70RSI.iterrows():
    print(index, row['rsi'])

import pandas as pd

df = pd.read_csv(
    '/Users/hbb/MyDocs/Work/Startup/KiteAPI/TickData/20211217/738561-20211217.csv',
    parse_dates=['ExcTS', 'LastTradeTS'],
    index_col=['ExcTS']
)

df.info()
print(df.head())
candlestickDF = df['LastPrice'].resample('1Min').ohlc()

print(candlestickDF.info())

print(candlestickDF.loc['2021-12-17 09:00:00':'2021-12-17 16:00:00'])

candlestickDF.to_csv(
    '/Users/hbb/MyDocs/Work/Startup/KiteAPI/TickData/20211217/stick-738561-20211217-1min.csv')

import pandas as pd
from ta.momentum import RSIIndicator

from signal import Signal


def get_previous_candles(df: pd.DataFrame, index, n: int, include_index=False):
    '''
    Returns previous n candles from the given index in the DataFrame

    Parameters:
    df (DataFrame): DataFrame from which to return the previous candles
    index (DataFrame Index): DataFrame Index from which to return the previous candles
    n (int): Number of previous candles to return from index
    include_index (bool): If current index should be included in returned DataFrame

    Returns:
    DataFrame: Pandas dataframe with the previous n candles
    '''
    loc = df.index.get_loc(index)
    fromIdx = loc-n
    toIdx = loc+1 if include_index else loc
    return df.iloc[fromIdx:toIdx]


def get_next_candles(df: pd.DataFrame, index, n: int):
    '''
    Returns next n candles from the given index in the DataFrame

    Parameters:
    df (DataFrame): DataFrame from which to return the next candles
    index (DataFrame Index): DataFrame Index from which to return the next candles
    n (int): Number of next candles to return from index

    Returns:
    DataFrame: Pandas dataframe with the next n candles
    '''
    loc = df.index.get_loc(index)
    return df.iloc[loc+1:loc+1+n]


def get_hourly_df(df: pd.DataFrame, index) -> pd.DataFrame:
    df_temp = df[:index]
    # print(index)
    # print(df_15min_temp.tail(10))
    df_60min_o = df_temp['Open'].resample(
        '60Min', offset='30Min').apply({'Open': 'first'})
    df_60min_h = df_temp['High'].resample(
        '60Min', offset='30Min').apply({'High': 'max'})
    df_60min_l = df_temp['Low'].resample(
        '60Min', offset='30Min').apply({'Low': 'min'})
    df_60min_c = df_temp['Close'].resample(
        '60Min', offset='30Min').apply({'Close': 'last'})
    df_60min_vol = df_temp['Volume'].resample(
        '60Min', offset='30Min').apply({'Volume': 'sum'})

    df_60min = pd.concat([df_60min_o, df_60min_h, df_60min_l,
                         df_60min_c, df_60min_vol], axis=1)
    df_60min.dropna(subset=['Open'], inplace=True)

    rsi = RSIIndicator(df_60min['Close']).rsi()
    df_60min = df_60min.assign(rsi=rsi.values)
    return df_60min


def get_tanaji_pct(df: pd.DataFrame, index, n: int, high: float) -> float:
    prev_candles = get_previous_candles(df, index, n)
    min_low = prev_candles['Low'].min()
    daily_movement = high - min_low
    tanaji_pct = (daily_movement/min_low)*100
    return tanaji_pct


def get_sell_tanaji_pct(df: pd.DataFrame, index, n: int, low: float) -> float:
    prev_candles = get_previous_candles(df, index, n)
    max_high = prev_candles['High'].max()
    daily_movement = max_high - low
    tanaji_pct = (daily_movement/max_high)*100
    return tanaji_pct


def generate_buy_signal_pnl(signal: Signal, df: pd.DataFrame, stop_gain: int) -> None:
    df = df[signal.ts:].copy()
    df.drop(index=df.index[0], axis=0, inplace=True)
    rnum = 0
    stop_loss_gap = signal.entry_price - signal.stop_loss
    rsi_breached = False

    for index, row in df.iterrows():
        if (row['Low'] < signal.stop_loss):
            #print('rnum: {}, index: {}, low: {}, sl: {}'.format(rnum, index, row['Low'], signal.stop_loss))
            signal.pnl = -1 * (signal.entry_price -
                               signal.stop_loss) * signal.lot_size
            signal.comment = "Stop Loss Breached at {}".format(index)
            break

        if ((row['High'] - signal.entry_price) * signal.lot_size >= stop_gain):
            signal.pnl = stop_gain
            signal.comment = "Stop Gain reached at {}".format(index)
            break

        if (rsi_breached == True):
            signal.pnl = (row['Open'] - signal.entry_price) * signal.lot_size
            signal.comment = "RSI Breached at {}".format(index)
            break

        if (row['High'] - signal.stop_loss > 2*stop_loss_gap):
            # print('New Stoploss: {}, Old Stoploss: {}, Stoploss gap: {}'.format(                row['High'] - stop_loss_gap, signal.stop_loss, stop_loss_gap))
            # signal.stop_loss = row['High'] - stop_loss_gap
            signal.stop_loss = signal.stop_loss

        if (row['rsi'] < 70 and row['Volume'] > 2*row['vol_sma5']):
            rsi_breached = True

        if(rnum > 50):
            signal.pnl = (row['Close'] -
                          signal.entry_price) * signal.lot_size
            # print('Signal failed to generate PnL: {}'.format(signal.pnl))
            signal.comment = "Signal failed to generate {}".format(index)
            break

        rnum = rnum+1


def generate_sell_signal_pnl(signal: Signal, df: pd.DataFrame, stop_gain: float) -> None:
    df = df[signal.ts:].copy()
    df.drop(index=df.index[0], axis=0, inplace=True)
    rnum = 0
    for index, row in df.iterrows():
        if (row['High'] > signal.stop_loss):
            #print('rnum: {}, index: {}, low: {}, sl: {}'.format(rnum, index, row['Low'], signal.stop_loss))
            signal.pnl = (signal.entry_price -
                          signal.stop_loss) * signal.lot_size
            break

        if ((signal.entry_price - row['Low']) * signal.lot_size >= stop_gain):
            signal.pnl = stop_gain
            break

        if(rnum > 50):
            signal.pnl = (signal.entry_price - row['Close']) * signal.lot_size
            # print('Signal failed to generate PnL: {}'.format(signal.pnl))
            break
        rnum = rnum+1

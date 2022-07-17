import pandas as pd


def get_hourly_df(df: pd.DataFrame, offset: str = '15Min') -> pd.DataFrame:
    df_temp = df[:]
    df_60min_o = df_temp['Open'].resample(
        '60Min', offset=offset).apply({'Open': 'first'})
    df_60min_h = df_temp['High'].resample(
        '60Min', offset=offset).apply({'High': 'max'})
    df_60min_l = df_temp['Low'].resample(
        '60Min', offset=offset).apply({'Low': 'min'})
    df_60min_c = df_temp['Close'].resample(
        '60Min', offset=offset).apply({'Close': 'last'})
    df_60min_vol = df_temp['Volume'].resample(
        '60Min', offset=offset).apply({'Volume': 'sum'})

    df_60min = pd.concat([df_60min_o, df_60min_h, df_60min_l,
                         df_60min_c, df_60min_vol], axis=1)
    df_60min.dropna(subset=['Open'], inplace=True)

    return df_60min


def get_30min_df(df: pd.DataFrame, offset: str = '0Min') -> pd.DataFrame:
    df_temp = df[:]
    df_30min_o = df_temp['Open'].resample(
        '30Min', offset=offset).apply({'Open': 'first'})
    df_30min_h = df_temp['High'].resample(
        '30Min', offset=offset).apply({'High': 'max'})
    df_30min_l = df_temp['Low'].resample(
        '30Min', offset=offset).apply({'Low': 'min'})
    df_30min_c = df_temp['Close'].resample(
        '30Min', offset=offset).apply({'Close': 'last'})
    df_30min_vol = df_temp['Volume'].resample(
        '30Min', offset=offset).apply({'Volume': 'sum'})

    df_30min = pd.concat([df_30min_o, df_30min_h, df_30min_l,
                         df_30min_c, df_30min_vol], axis=1)
    df_30min.dropna(subset=['Open'], inplace=True)

    return df_30min


def get_15min_df(df: pd.DataFrame, offset: str = '0Min') -> pd.DataFrame:
    df_temp = df[:]
    df_15min_o = df_temp['Open'].resample(
        '15Min', offset=offset).apply({'Open': 'first'})
    df_15min_h = df_temp['High'].resample(
        '15Min', offset=offset).apply({'High': 'max'})
    df_15min_l = df_temp['Low'].resample(
        '15Min', offset=offset).apply({'Low': 'min'})
    df_15min_c = df_temp['Close'].resample(
        '15Min', offset=offset).apply({'Close': 'last'})
    df_15min_vol = df_temp['Volume'].resample(
        '15Min', offset=offset).apply({'Volume': 'sum'})

    df_15min = pd.concat([df_15min_o, df_15min_h, df_15min_l,
                         df_15min_c, df_15min_vol], axis=1)
    df_15min.dropna(subset=['Open'], inplace=True)

    return df_15min

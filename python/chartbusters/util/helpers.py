import pandas as pd


def get_revised_interval_df(df: pd.DataFrame, new_interval: str, offset: str) -> pd.DataFrame:
    df_temp = df[:]

    df_open = df_temp['Open'].resample(
        new_interval, offset=offset).apply({'Open': 'first'})
    df_high = df_temp['High'].resample(
        new_interval, offset=offset).apply({'High': 'max'})
    df_low = df_temp['Low'].resample(
        new_interval, offset=offset).apply({'Low': 'min'})
    df_close = df_temp['Close'].resample(
        new_interval, offset=offset).apply({'Close': 'last'})
    df_vol = df_temp['Volume'].resample(
        new_interval, offset=offset).apply({'Volume': 'sum'})

    df_new_interval = pd.concat([df_open, df_high, df_low,
                                 df_close, df_vol], axis=1)
    df_new_interval.dropna(subset=['Open'], inplace=True)

    return df_new_interval

import pandas as pd


def get_previous_candles(df, index, n, include_index=False):
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


def get_next_candles(df, index, n):
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

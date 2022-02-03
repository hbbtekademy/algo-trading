from __future__ import annotations
from typing import List
import pandas as pd
import pandas_ta as ta
from ChartBusters import constants
from ChartBusters.cb_candle import CBCandle
from ta.momentum import RSIIndicator
from ta.trend import ADXIndicator
from ta.trend import MACD


class CBChart():
    def __init__(self, sym: str, lot_size: int, df: pd.DataFrame, sma_interval: int = 5, ema_interval: int = 10) -> None:
        self.sym = sym
        self.lot_size = lot_size
        self.df = df
        self.__calc_indicators(sma_interval, ema_interval)

    def __calc_indicators(self, sma_interval: int, ema_interval: int, sti_interval: int = 10, sti_multiplier: int = 2) -> None:
        self.__sma_interval = int(sma_interval)
        self.__ema_interval = int(ema_interval)
        self.__sti_interval = int(sti_interval)
        self.__sti_multiplier = int(sti_multiplier)
        self.__calc_rsi()
        self.__calc_adx2()
        self.__calc_macd()
        self.__calc_supertrend()
        self.__calc_sma(sma_interval)
        self.__calc_ema(ema_interval)

    def __calc_rsi(self) -> None:
        rsi = RSIIndicator(self.df['Close']).rsi()
        self.df[constants.RSI] = rsi.values

    def __calc_adx(self) -> None:
        adx = ADXIndicator(high=self.df['High'],
                           low=self.df['Low'], close=self.df['Close'])

        self.df[constants.ADX] = adx.adx().values
        self.df[constants.ADX_POS] = adx.adx_pos().values
        self.df[constants.ADX_NEG] = adx.adx_neg().values

    def __calc_adx2(self) -> None:
        adx_df = ta.adx(high=self.df['High'], low=self.df['Low'],
                        close=self.df['Close'])

        self.df[constants.ADX] = adx_df.iloc[:, 0].values
        self.df[constants.ADX_POS] = adx_df.iloc[:, 1].values
        self.df[constants.ADX_NEG] = adx_df.iloc[:, 2].values

    def __calc_macd(self) -> None:
        macd = MACD(self.df['Close'])
        self.df[constants.MACD] = macd.macd().values
        self.df[constants.MACD_SIG] = macd.macd_signal().values
        self.df[constants.MACD_DIFF] = macd.macd_diff().values

    def __calc_supertrend(self) -> None:
        sti = ta.supertrend(
            self.df[constants.HIGH], self.df[constants.LOW], self.df[constants.CLOSE], self.__sti_interval, self.__sti_multiplier)

        self.df[constants.STI_TREND] = sti.iloc[:, 0].values
        self.df[constants.STI_DIR] = sti.iloc[:, 1].values
        self.df[constants.STI_LONG] = sti.iloc[:, 2].values
        self.df[constants.STI_SHORT] = sti.iloc[:, 3].values

    def __calc_sma(self, interval: int) -> None:
        open_sma = self.df[constants.OPEN].rolling(interval).mean()
        self.df[constants.SMA_OPEN] = open_sma.values

        high_sma = self.df[constants.HIGH].rolling(interval).mean()
        self.df[constants.SMA_HIGH] = high_sma.values

        low_sma = self.df[constants.LOW].rolling(interval).mean()
        self.df[constants.SMA_LOW] = low_sma.values

        close_sma = self.df[constants.CLOSE].rolling(interval).mean()
        self.df[constants.SMA_CLOSE] = close_sma.values

        vol_sma = self.df[constants.VOL].rolling(interval).mean()
        self.df[constants.SMA_VOL] = vol_sma.values

    def __calc_ema(self, interval: int) -> None:
        open_ema = self.df[constants.OPEN].ewm(
            span=interval, adjust=False).mean()
        self.df[constants.EMA_OPEN] = open_ema.values

        high_ema = self.df[constants.HIGH].ewm(
            span=interval, adjust=False).mean()
        self.df[constants.EMA_HIGH] = high_ema.values

        low_ema = self.df[constants.LOW].ewm(
            span=interval, adjust=False).mean()
        self.df[constants.EMA_LOW] = low_ema.values

        close_ema = self.df[constants.CLOSE].ewm(
            span=interval, adjust=False).mean()
        self.df[constants.EMA_CLOSE] = close_ema.values

        vol_ema = self.df[constants.VOL].ewm(
            span=interval, adjust=False).mean()
        self.df[constants.EMA_VOL] = vol_ema.values

    def candle(self, ts) -> CBCandle:
        row = self.df.loc[ts]
        return CBCandle(self.sym, row)

    def previous(self, current_candle: CBCandle) -> CBCandle:
        loc = self.df.index.get_loc(current_candle.ts)
        row = self.df.iloc[loc-1]
        return CBCandle(self.sym, row)

    def sub_chart(self, start_ts, end_ts) -> List[CBCandle]:
        candles = list()
        df = self.df[start_ts:end_ts]
        for _, row in df.iterrows():
            candle = CBCandle(self.sym, row)
            candles.append(candle)

        return candles

    def get_previous_candles(self, index, n: int, include_index: bool = False) -> List[CBCandle]:
        candles = list()
        loc = self.df.index.get_loc(index)
        fromIdx = loc-n
        toIdx = loc+1 if include_index else loc

        df = self.df.iloc[fromIdx:toIdx]
        for _, row in df.iterrows():
            candle = CBCandle(self.sym, row)
            candles.append(candle)

        return candles

    def get_next_candles(self, index, n: int) -> List[CBCandle]:
        candles = list()
        loc = self.df.index.get_loc(index)

        df = self.df.iloc[loc+1:loc+1+n]
        for _, row in df.iterrows():
            candle = CBCandle(self.sym, row)
            candles.append(candle)

        return candles

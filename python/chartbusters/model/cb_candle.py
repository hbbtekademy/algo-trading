import pandas as pd

from python.chartbusters.util import constants


class CBCandle:
    def __init__(self, sym: str, row: pd.Series, MA: str = constants.EMA) -> None:
        self.__row = row
        self.sym = sym
        self.ts = row.name

        self.open = row[constants.OPEN]
        self.high = row[constants.HIGH]
        self.low = row[constants.LOW]
        self.close = row[constants.CLOSE]
        self.vol = row[constants.VOL]

        self.rsi = row[constants.RSI]
        # self.rsi_60 = row[constants.RSI_60]

        self.adx = row[constants.ADX]
        self.adx_neg = row[constants.ADX_NEG]
        self.adx_pos = row[constants.ADX_POS]

        self.macd = row[constants.MACD]
        self.macd_sig = row[constants.MACD_SIG]
        self.macd_diff = row[constants.MACD_DIFF]

        self.sti_trend = row[constants.STI_TREND]
        self.sti_dir = row[constants.STI_DIR]
        self.sti_long = row[constants.STI_LONG]
        self.sti_short = row[constants.STI_SHORT]

        self.sma_open = row[constants.SMA_OPEN]
        self.sma_high = row[constants.SMA_HIGH]
        self.sma_low = row[constants.SMA_LOW]
        self.sma_close = row[constants.SMA_CLOSE]
        self.sma_vol = row[constants.SMA_VOL]

        self.ema_open = row[constants.EMA_OPEN]
        self.ema_high = row[constants.EMA_HIGH]
        self.ema_low = row[constants.EMA_LOW]
        self.ema_close = row[constants.EMA_CLOSE]
        self.ema_vol = row[constants.EMA_VOL]

        if MA == constants.SMA:
            self.ma_open = row[constants.SMA_OPEN]
            self.ma_high = row[constants.SMA_HIGH]
            self.ma_low = row[constants.SMA_LOW]
            self.ma_close = row[constants.SMA_CLOSE]
            self.ma_vol = row[constants.SMA_VOL]
        elif MA == constants.EMA:
            self.ma_open = row[constants.EMA_OPEN]
            self.ma_high = row[constants.EMA_HIGH]
            self.ma_low = row[constants.EMA_LOW]
            self.ma_close = row[constants.EMA_CLOSE]
            self.ma_vol = row[constants.EMA_VOL]

    def __str__(self) -> str:
        return 'Sym: {}, TS: {}, O: {}, H: {}, L: {}, C: {}, Vol: {}, RSI: {}, ADX: {}'.format(self.sym, self.ts,
                                                                                               self.open, self.high,
                                                                                               self.low, self.close,
                                                                                               self.vol,
                                                                                               self.rsi, self.adx)

    # clarify with Sameer Bhate - why is 1015, 1115, etc start of hour.
    # Also, this method is tightly coupled to Indian equity market. Need to read these constants from a config or DB.
    # the constants must be an attribute of the market on which the startegy must run.
    def is_start_of_hr(self) -> bool:
        ts = str(self.ts)
        if ts.find('09:15:00') != -1:
            return True
        if ts.find('10:15:00') != -1:
            return True
        if ts.find('11:15:00') != -1:
            return True
        if ts.find('12:15:00') != -1:
            return True
        if ts.find('13:15:00') != -1:
            return True
        if ts.find('14:15:00') != -1:
            return True

        return False

    def is_end_of_hr(self) -> bool:
        ts = str(self.ts)
        if ts.find('10:00:00') != -1:
            return True
        if ts.find('11:00:00') != -1:
            return True
        if ts.find('12:00:00') != -1:
            return True
        if ts.find('13:00:00') != -1:
            return True
        if ts.find('14:00:00') != -1:
            return True
        if ts.find('15:00:00') != -1:
            return True

        return False

    def is_last_candle(self) -> bool:
        ts = str(self.ts)
        if ts.find('15:15:00') != -1:
            return True

        return False

    def is_sod_candle(self) -> bool:
        ts = str(self.ts)

        if ts.find('09:00:00') != -1:
            return True
        if ts.find('09:15:00') != -1:
            return True

        return False

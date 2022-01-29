import pandas as pd
from ChartBusters import constants


class CBCandle():
    def __init__(self, sym: str, row: pd.core.series.Series) -> None:
        self.__row = row
        self.sym = sym
        self.ts = row.name

        self.open = row[constants.OPEN]
        self.high = row[constants.HIGH]
        self.low = row[constants.LOW]
        self.close = row[constants.CLOSE]
        self.vol = row[constants.VOL]

        self.rsi = row[constants.RSI]
        #self.rsi_60 = row[constants.RSI_60]

        self.adx = row[constants.ADX]
        self.adx_neg = row[constants.ADX_NEG]
        self.adx_pos = row[constants.ADX_POS]

        self.macd = row[constants.MACD]
        self.macd_sig = row[constants.MACD_SIG]
        self.macd_diff = row[constants.MACD_DIFF]

    def __str__(self) -> str:
        return 'Sym: {}, TS: {}, O: {}, H: {}, L: {}, C: {}, Vol: {}, RSI: {}, ADX: {}'.format(self.sym, self.ts,
                                                                                               self.open, self.high, self.low, self.close, self.vol,
                                                                                               self.rsi, self.adx)

from typing import List
import pandas as pd

header = 'Date,Open,High,Low,Close,Volume'


def write_ohlc_to_file(fn: str, hist_ohlc: List) -> bool:
    if hist_ohlc is not None and len(hist_ohlc) > 0:
        with open(fn, 'w+') as file:
            file.write(header + '\n')

            for ohlc in hist_ohlc:
                line = ohlc['datetime'] + ',' + ohlc['open'] + ',' + ohlc['high'] + \
                       ',' + ohlc['low'] + ',' + \
                       ohlc['close'] + ',' + ohlc['volume']
                file.write(line + '\n')
        return True
    else:
        return False

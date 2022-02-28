from typing import List
import pandas as pd


def write_ohlc_to_file(fn: str, hist_ohlc: List) -> bool:
    if (len(hist_ohlc) > 0):
        with open(fn, 'w+') as file1:
            header = 'Date,Open,High,Low,Close,Volume'
            # print(header)
            file1.write(header + '\n')

            for ohlc in hist_ohlc:
                line = ohlc['datetime'] + ',' + ohlc['open'] + ',' + ohlc['high'] + \
                    ',' + ohlc['low'] + ',' + \
                    ohlc['close'] + ',' + ohlc['volume']
                # print(line)
                file1.write(line + '\n')
        return True
    else:
        return False

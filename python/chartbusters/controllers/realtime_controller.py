import time
from datetime import datetime

import pandas as pd
import redis

from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v1 import CBSignalV1
from python.chartbusters.strategies.rsi.cb_rsi_adx_buy_or_sell_strategy import RsiAdxBuyOrSellStrategy
from python.chartbusters.strategies.supertrend.basic.cb_supertrend_strategy import CBSuperTrendStrategy
from python.chartbusters.util import helpers


class RealtimeExecutor:

    def __init__(self, driver_file, strategy_params_dict):
        self.driver_file = driver_file
        self.strategy_params_dict = strategy_params_dict

    def connect_to_realtime_datasource(self):
        pass

    def get_data_frame(self):
        pass

    def execute_strategy(self):
        pass

    def broadcast_signal(self):
        pass

    def record_signal(self):
        pass

    def execute(self, strategy_name) -> str:
        print('Real Time execution')
        # 1. read from redis topic CS1M - at 15 min mark
        redis_realtime_db = redis.StrictRedis(host='localhost', port=6379, db=1,
                                              charset="utf-8", decode_responses=True)
        redis_historical_db = redis.StrictRedis(host='localhost', port=6379, db=0,
                                                charset="utf-8", decode_responses=True)
        p = redis_realtime_db.pubsub()
        p.subscribe('CS1M_NOTIFY')
        df_15min_hist = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        historical_candlestick_keys_list = redis_historical_db.keys('CS15M*')
        for hist_candle in historical_candlestick_keys_list:
            ohlcv_hist = redis_historical_db.hgetall(hist_candle)
            datetime_str = hist_candle[12:24]
            date_time_obj = datetime.strptime(datetime_str, '%Y%m%d%H%M')
            df_hist = pd.DataFrame({"Date": date_time_obj,
                                    "Open": [ohlcv_hist.get('O')],
                                    "High": [ohlcv_hist.get('H')],
                                    "Low": [ohlcv_hist.get('L')],
                                    "Close": [ohlcv_hist.get('C')],
                                    "Volume": [ohlcv_hist.get('V')]})
            df_15min_hist = df_15min_hist.append(df_hist)

        for _ in iter(int, 1):
            time.sleep(3)
            message = p.get_message()
            df_1min_realtime = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            if message:
                print(message)

                # read today's 1-min candles
                candlestick_keys_list = redis_realtime_db.keys('CS1M*')
                for candle in candlestick_keys_list:
                    ohlcv = redis_realtime_db.hgetall(candle)
                    print(ohlcv)
                    datetime_str = candle[12:24]
                    date_time_obj = datetime.strptime(datetime_str, '%Y%m%d%H%M')
                    df1 = pd.DataFrame({"Date": date_time_obj,
                                        "Open": [float(ohlcv.get('O'))],
                                        "High": [float(ohlcv.get('H'))],
                                        "Low": [float(ohlcv.get('L'))],
                                        "Close": [float(ohlcv.get('C'))],
                                        "Volume": [int(ohlcv.get('V'))]})
                    df_1min_realtime = df_1min_realtime.append(df1)
                print(df_1min_realtime)
                df_1min_realtime['Date'] = pd.to_datetime(df_1min_realtime['Date'], errors='coerce')
                print('df_1min_realtime:')
                print(df_1min_realtime)
                df_1min_realtime = df_1min_realtime.set_index('Date')
                df_15min_realtime = helpers.get_revised_interval_df(df_1min_realtime, '15Min', '1Min')
                if df_15min_hist.empty:
                    df_15min_merged = df_15min_realtime
                else:
                    df_15min_merged = df_15min_hist.append(df_15min_realtime, ignore_index=True)
                print('df_15min_merged:')
                print(df_15min_merged)
                cb_chart = self.get_cbchart(df_15min_merged, "9999", "100", strategy_name)
                row = {'Expiry': 'TBD',
                       'StopLoss15': '1000'}
                strategy = self.get_strategy(row, cb_chart, strategy_name)
                signal = CBSignalV1('', '', 0, '', 0, 0, None)
                date_time_obj = datetime.strptime('202208111501', '%Y%m%d%H%M')
                print('date_time_obj:', date_time_obj)
                exec_result, signal = strategy.execute(cb_chart.candle(date_time_obj), signal)
                print('exec_result: ', exec_result)
                print('signal: ', signal)
                pub_result = redis_historical_db.publish('Smash-Telegram-Channel', signal.__str__())
                print('pub_result: ', pub_result)
                pass
        # 2. Read Candlestick data from Redis DB (and Hist DB)
        # 3. Combine it into a Data Frame
        # 4. Execute Strategy

        pass

    def get_cbchart(self, df, symbol, lot_size, strategy_name):

        if strategy_name == 'STI':
            return CBChart(symbol, lot_size
                           , df, ema_interval=self.get_strategy_param_value('ema_interval'),
                           sma_interval=self.get_strategy_param_value('sma_interval'),
                           MA=self.get_strategy_param_value('MA'),
                           sti_interval=self.get_strategy_param_value('sti_interval'),
                           sti_multiplier=self.get_strategy_param_value('sti_multiplier'))

        if strategy_name == 'RSI-BUY':
            return CBChart(symbol, lot_size, df, ema_interval=self.get_strategy_param_value('ema_interval'))

    def get_strategy_param_value(self, strategy_param_key):
        return self.strategy_params_dict.get(strategy_param_key).get(0)

    def get_strategy(self, row, cb_chart, strategy_name):

        if strategy_name == 'STI':
            expiry = row['Expiry']
            stoploss_margin = int(row['StopLoss15'])
            return CBSuperTrendStrategy('SuperTrend15',
                                        cb_chart, expiry,
                                        stoploss_margin=stoploss_margin,
                                        supertrend_ma_margin=self.get_strategy_param_value('supertrend_ma_margin'),
                                        stoploss_gap=self.get_strategy_param_value('stoploss_gap'))

        if strategy_name == 'RSI-BUY':
            return RsiAdxBuyOrSellStrategy(
                cb_chart, float(row['StopLoss']), float(row['StopGain']), True, float(row['RSI']), float(row['ADXMin']),
                float(row['ADXMax']))

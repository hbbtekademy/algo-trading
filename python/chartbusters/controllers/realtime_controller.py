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

    def execute(self, strategy_name, stock_symbol) -> str:
        redis_realtime_db = self.get_redis_client(1)
        redis_historical_db = self.get_redis_client(0)

        pub_sub_client = redis_realtime_db.pubsub()
        pub_sub_client.subscribe('CS1M_NOTIFY')

        df_1min_hist = self.get_data_frame_from_db(redis_historical_db)

        for _ in iter(int, 1):
            time.sleep(3)
            message = pub_sub_client.get_message()
            if message:
                print(message)
                df_1min_realtime = self.get_data_frame_from_db(redis_realtime_db)
                df_1min_merged = df_1min_hist.append(df_1min_realtime, ignore_index=False)
                print('df_1min_hist', df_1min_hist)
                print('df_1min_realtime', df_1min_realtime)
                print('df_1min_merged', df_1min_merged)
                df_15min_merged = helpers.get_revised_interval_df(df_1min_merged, '15Min', '1Min')

                cb_chart = self.get_cbchart(df_15min_merged, stock_symbol, "100", strategy_name)
                row = self.get_strategy_params(strategy_name)
                strategy = self.get_strategy(row, cb_chart, strategy_name)
                signal = self.get_new_signal()
                latest_candle = cb_chart.get_last_candle()
                exec_result, signal = strategy.execute(latest_candle, signal)
                pub_result = redis_historical_db.publish('Smash-Telegram-Channel', signal.__str__())
                print('pub_result: ', pub_result)
                pass
            else:
                print('No Message in last 3 seconds')
        pass

    @staticmethod
    def get_new_signal():
        signal = CBSignalV1('', '', 0, '', 0, 0, None)
        return signal

    @staticmethod
    def get_strategy_params(strategy_name):
        if strategy_name == 'STI':
            # TODO: Check with Bhate - Where is this defined?
            return {'Expiry': 'TBD',
                    'StopLoss15': '1000'}
        else:
            return 'Undefined Strategy'

    @staticmethod
    def get_data_frame_from_db(redis_db_client):
        df_1min = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        candlestick_keys_list = redis_db_client.keys('CS1M*')
        for candle in candlestick_keys_list:
            ohlcv_object = redis_db_client.hgetall(candle)
            datetime_str = candle[12:24]
            date_time_obj = datetime.strptime(datetime_str, '%Y%m%d%H%M')
            df_element = pd.DataFrame({"Date": date_time_obj,
                                       "Open": [float(ohlcv_object.get('O'))],
                                       "High": [float(ohlcv_object.get('H'))],
                                       "Low": [float(ohlcv_object.get('L'))],
                                       "Close": [float(ohlcv_object.get('C'))],
                                       "Volume": [int(ohlcv_object.get('V'))]})
            df_1min = df_1min.append(df_element)
        df_1min['Date'] = pd.to_datetime(df_1min['Date'], errors='coerce')
        df_1min = df_1min.set_index('Date')
        return df_1min

    @staticmethod
    def get_redis_client(db):
        redis_realtime_db = redis.StrictRedis(host='localhost', port=6379, db=db,
                                              charset="utf-8", decode_responses=True)
        return redis_realtime_db

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

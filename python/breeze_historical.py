import os
import sys

import pandas as pd
from breeze_connect import BreezeConnect

from chartbusters import helpers
from chartbusters.breeze_api import breeze_helpers

STOCK_CODE = 'NIFTY'
FROM_DATE = '2022-01-01T00:00:00.000Z'
TO_DATE = '2022-03-31T00:00:00.000Z'
EXPIRY_DATE = '2022-04-28T07:00:00.000Z'
INTERVAL = '5minute'

API_KEY = os.getenv('BREEZE_API_KEY')
API_SECRET = os.getenv('BREEZE_API_SECRET')
SESSION_TOKEN = os.getenv('BREEZE_API_SESSION')

if not API_KEY:
    print("BREEZE_API_KEY env not set. Exiting...")
    sys.exit(1)

if not API_SECRET:
    print("BREEZE_API_SECRET env not set. Exiting...")
    sys.exit(1)

if not SESSION_TOKEN:
    print("BREEZE_API_SESSION env not set. Exiting...")
    sys.exit(1)

isec = BreezeConnect(api_key=API_KEY)

isec.generate_session(api_secret=API_SECRET, session_token=SESSION_TOKEN)

hist_resp = isec.get_historical_data(interval=INTERVAL, from_date=FROM_DATE, to_date=TO_DATE,
                                     stock_code=STOCK_CODE, exchange_code='NFO',
                                     product_type='Futures', expiry_date=EXPIRY_DATE, strike_price='0')


if hist_resp['Status'] != 200:
    print('Failed getting historical data. Status: ' +
          str(hist_resp['Status']) + '. Error: ' + hist_resp['Error'])
else:
    hist_ohlc = hist_resp['Success']
    fn5m = STOCK_CODE + '-5M.csv'
    fn15m = STOCK_CODE + '-15M.csv'
    rc = breeze_helpers.write_ohlc_to_file(fn5m, hist_ohlc=hist_ohlc)
    if rc:
        df = pd.read_csv(fn5m, parse_dates=['Date'], index_col=['Date'])

        df_15min = helpers.get_15min_df(df)
        df_15min.to_csv(fn15m, date_format='%Y-%m-%dT%H:%M:%S+05:30')
        print(df_15min)
    else:
        print('Historical data not available...')

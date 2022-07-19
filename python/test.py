import pandas as pd

dict_from_csv = pd.read_csv('backtest/config/strategy_parameters/sti_params_v2.csv',
                            header=0, index_col=False).to_dict()
print('here...')
print(dict_from_csv)
print(dict_from_csv.get('ema_interval').get(0))
print(dict_from_csv.get('ema_interval').get(1))

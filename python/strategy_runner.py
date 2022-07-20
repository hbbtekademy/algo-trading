import pandas as pd

from python.chartbusters.controllers.backtest_controller import BacktestExecutor
from python.chartbusters.controllers.realtime_controller import RealtimeExecutor

strategy = input("Select strategies. Options - STI,RSI-BUY,RSI-SELL. Enter:")
print("strategies is:", strategy)

execution_mode = input("Select Execution Mode. options: RT or BT. Enter:")
print("execution_mode is:", execution_mode)


def get_driver_file(strategy_name: str):
    if strategy_name == 'STI':
        return 'backtest/config/driver_files/STI_NiftyFut_Verify.csv'
    if strategy_name == 'RSI-BUY':
        return 'backtest/config/driver_files/RSI_ADX_Buy_BackTest.csv'
    if strategy_name == 'RSI-SELL':
        return 'backtest/config/driver_files/RSI_ADX_Sell_BackTest.csv'


def get_param_file(strategy_name: str):
    if strategy_name == 'STI':
        return 'backtest/config/strategy_parameters/sti_params.csv'
    if strategy_name == 'RSI-BUY':
        return 'backtest/config/strategy_parameters/rsi_buy_params.csv'
    if strategy_name == 'RSI-SELL':
        return 'backtest/config/strategy_parameters/rsi_sell_params.csv'


def get_strategy_params_dict(parameter_file):
    return pd.read_csv(parameter_file,
                       header=0, index_col=False).to_dict()


if execution_mode == 'RT':
    print('Executing in Real Time mode')
    rte = RealtimeExecutor()
    rte.execute()
elif execution_mode == 'BT' or 1 == 1:
    print('Executing in Back Test mode')
    driver_file = get_driver_file(strategy)
    strategy_params_dict = get_strategy_params_dict(get_param_file(strategy))
    bte = BacktestExecutor(driver_file,  strategy_params_dict)
    result = bte.execute(strategy)
    print('Result', result)
else:
    print('Execution mode not recognized.')

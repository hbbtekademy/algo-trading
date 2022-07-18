from python.chartbusters.controllers.backtest_controller import BacktestExecutor
from python.chartbusters.controllers.realtime_controller import RealtimeExecutor

strategy = input("Select strategies. Options - STI,RSI-BUY,RSI-SELL. Enter:")
print("strategies is:", strategy)

execution_mode = input("Select Execution Mode. options: RT or BT. Enter:")
print("execution_mode is:", execution_mode)


def get_driver_file(strategy_name: str):
    if strategy_name == 'STI':
        return 'backtest/config/STI_NiftyFut_Verify.csv'
    if strategy_name == 'RSI-BUY':
        return 'backtest/config/RSI_ADX_Buy_BackTest.csv'
    if strategy_name == 'RSI-SELL':
        return 'backtest/config/RSI_ADX_Sell_BackTest.csv'


if execution_mode == 'RT':
    print('Executing in Real Time mode')
    rte = RealtimeExecutor()
    rte.execute()
elif execution_mode == 'BT' or 1 == 1:
    print('Executing in Back Test mode')
    driver_file = get_driver_file(strategy)
    bte = BacktestExecutor(driver_file)
    result = bte.execute('invoked')
    print('Result', result)
else:
    print('Execution mode not recognized.')

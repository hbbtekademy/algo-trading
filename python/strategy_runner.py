from python.chartbusters.controllers.backtest_controller import BacktestExecutor
from python.chartbusters.controllers.realtime_controller import RealtimeExecutor

strategy = input("Select strategies. Options - STI,RSI. Enter:")
print("strategies is:", strategy)

execution_mode = input("Select Execution Mode. options: RT or BT. Enter:")
print("execution_mode is:", execution_mode)

if execution_mode == 'RT':
    print('Executing in Real Time mode')
    rte = RealtimeExecutor()
    rte.execute()

elif execution_mode == 'BT' or 1 == 1:
    print('Executing in Back Test mode')
    driver_file = 'backtest/config/STI_NiftyFut_Verify.csv'
    bte = BacktestExecutor(driver_file, 50, 'NIFTY22JUNFUT')
    result = bte.execute('invoked')
    print('Result', result)
else:
    print('Execution mode not recognized.')

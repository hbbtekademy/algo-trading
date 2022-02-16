from ChartBusters.Strategy.cb_strategy import CBStrategy
from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_candle import CBCandle
from ChartBusters.Strategy.cb_strategy_result import CBStrategyResult
from ChartBusters.cb_signal import CBSignal
from typing import List, Tuple


class CBSuperTrendStrategy(CBStrategy):
    def __init__(self, strategy: str, chart: CBChart, expiry, stoploss_margin: int = 120, supertrend_ma_margin: int = 30,
                 stoploss_gap: int = 20) -> None:
        super().__init__(chart)
        self.strategy = strategy
        self.stoploss_margin = stoploss_margin
        self.stoploss_gap = stoploss_gap
        self.supertrend_ma_margin = supertrend_ma_margin
        self.stop_gain = 200000000
        self.expiry = expiry
        self.expiry_ts = self.expiry + ' 15:00:00+05:30'
        self.expiry_ts2 = self.expiry + ' 15:15:00+05:30'

        if(self.strategy == 'SuperTrend60'):
            self.expiry_ts = self.expiry + ' 14:15:00+05:30'

    def execute(self, candle: CBCandle, signal: CBSignal) -> Tuple[str, CBSignal]:
        prev_candle = self.chart.previous(candle)
        rsi = candle.rsi

        stop_loss_updated_ema = False
        if(str(candle.ts) == self.expiry_ts2):
            return '', None

        # Series Expiry Signal Closure
        if(str(candle.ts) == self.expiry_ts):
            next_candle = self.chart.get_next_candles(candle.ts, 1)[0]
            if (signal.status == 'O'):
                signal.status = 'C'
                signal.exit_ts = next_candle.ts
                signal.exit_price = next_candle.open
                signal.pnl = round(
                    (signal.entry_price - next_candle.open)*signal.lot_size, 2)
                if signal.strategy == 'ST_Buy':
                    signal.pnl = -1 * signal.pnl
                signal.comment = signal.comment + 'Position squared off at expiry'

                return 'SL', None

        buy_ma_passed = candle.ma_close < candle.low or (
            candle.close > candle.open and candle.close > candle.ma_close and (candle.high-candle.low)/2 > candle.ma_close)
        sell_ma_passed = candle.ma_close > candle.high or (
            candle.close < candle.open and candle.close < candle.ma_close and (candle.high-candle.low)/2 < candle.ma_close)

        # if str(candle.ts).find('2022-01-21 09:') != -1:
        #    print(candle.ts, signal.status, signal.strategy)

        # Verify potential signals
        if (signal.strategy == 'P_Buy' and candle.sti_dir == 1):
            stop_loss_passed = abs(
                prev_candle.sti_trend - candle.low) <= self.stoploss_margin

            ma_sl = False
            entry_price = prev_candle.sti_trend + self.stoploss_margin
            if(candle.open <= entry_price):
                entry_price = candle.open

            if(stop_loss_passed):
                buy_stoploss = candle.sti_trend - self.stoploss_gap
                if candle.ma_close < candle.sti_trend and abs(candle.ma_close - candle.sti_trend) <= self.supertrend_ma_margin:
                    buy_stoploss = round(
                        candle.ma_close - self.stoploss_gap, 2)
                    ma_sl = True

                buy_signal = CBSignal(
                    'ST_Buy', self.chart.sym, self.chart.lot_size, candle.ts, entry_price, buy_stoploss, candle)
                buy_signal.sti_trend = round(signal.sti_trend, 2)
                buy_signal.ma_close = round(signal.ma_close, 2)
                buy_signal.ma_stoploss = ma_sl
                buy_signal.comment = buy_signal.comment + \
                    "Enter Buy. Prev ST: {} | Diff:{}".format(
                        round(prev_candle.sti_trend, 2), round(abs(prev_candle.sti_trend - entry_price), 2))
                return 'New', buy_signal

        if (signal.strategy == 'P_Sell' and candle.sti_dir == -1):
            stop_loss_passed = abs(
                prev_candle.sti_trend - candle.high) <= self.stoploss_margin

            ma_sl = False
            entry_price = prev_candle.sti_trend - self.stoploss_margin
            if(candle.open >= entry_price):
                entry_price = candle.open

            if(stop_loss_passed):
                sell_stoploss = candle.sti_trend + self.stoploss_gap
                if candle.ma_close > candle.sti_trend and abs(candle.ma_close - candle.sti_trend) <= self.supertrend_ma_margin:
                    sell_stoploss = round(
                        candle.ma_close + self.stoploss_gap, 2)
                    ma_sl = True

                sell_signal = CBSignal(
                    'ST_Sell', self.chart.sym, self.chart.lot_size, candle.ts, entry_price, sell_stoploss, candle)
                sell_signal.sti_trend = round(signal.sti_trend, 2)
                sell_signal.ma_close = round(signal.ma_close, 2)
                sell_signal.ma_stoploss = ma_sl
                sell_signal.comment = sell_signal.comment + \
                    "Enter Sell. Prev ST: {} | Diff:{}".format(
                        round(prev_candle.sti_trend, 2), round(abs(prev_candle.sti_trend - entry_price), 2))
                return 'New', sell_signal

        # Stop Loss Checks
        if (signal.strategy == 'ST_Buy' and signal.status == 'O'):
            comment = ''
            if (candle.low < signal.stop_loss):
                # print(candle.ts, signal.stop_loss, candle.low)
                signal.status = 'C'
                signal.exit_ts = candle.ts
                signal.exit_price = signal.stop_loss
                comment = ' StopLoss breached'
                if (candle.high < signal.stop_loss):
                    signal.exit_price = candle.open
                    comment = ' StopLoss breached. Gap down opening. PnL Impact: {}'.format(
                        round(abs(candle.open-signal.stop_loss)*signal.lot_size), 2)
                signal.pnl = round(-1 *
                                   (signal.entry_price - signal.exit_price)*signal.lot_size, 2)
                signal.comment = signal.comment + comment
                # return 'SL', None

        if (signal.strategy == 'ST_Sell' and signal.status == 'O'):
            comment = ''
            if(candle.high > signal.stop_loss):
                signal.status = 'C'
                signal.exit_ts = candle.ts
                signal.exit_price = signal.stop_loss
                comment = ' StopLoss breached'
                if (candle.low > signal.stop_loss):
                    signal.exit_price = candle.open
                    comment = ' StopLoss breached. Gap up opening. PnL Impact: {}'.format(
                        round(abs(candle.open-signal.stop_loss)*signal.lot_size), 2)
                signal.pnl = round(-1 *
                                   (signal.exit_price - signal.entry_price)*signal.lot_size, 2)
                signal.comment = signal.comment + comment
                # return 'SL', None

        # Profit Checks
        if (signal.strategy == 'ST_Sell' and signal.status == 'O'):
            if ((signal.entry_price - candle.low) * signal.lot_size >= self.stop_gain):
                signal.status = 'C'
                signal.pnl = self.stop_gain
                signal.exit_ts = candle.ts
                signal.exit_price = round(
                    signal.entry_price - self.stop_gain/signal.lot_size, 2)
                signal.comment = "Stop Gain reached"

        if (signal.strategy == 'ST_Buy' and signal.status == 'O'):
            if ((candle.high - signal.entry_price) * signal.lot_size >= self.stop_gain):
                signal.status = 'C'
                signal.pnl = self.stop_gain
                signal.exit_ts = candle.ts
                signal.exit_price = round(
                    self.stop_gain/signal.lot_size + signal.entry_price, 2)
                signal.comment = "Stop Gain reached"

        # Update Stop Loss
        if signal.strategy in ('ST_Buy', 'P_Buy') and signal.status != 'C' and candle.sti_dir == 1:
            signal.stop_loss = round(candle.sti_trend - self.stoploss_gap, 2)
            signal.ma_stoploss = False
            if candle.ma_close < candle.sti_trend and abs(candle.ma_close - candle.sti_trend) <= self.supertrend_ma_margin:
                signal.stop_loss = round(
                    candle.ma_close - self.stoploss_gap, 2)
                signal.ma_stoploss = True
            # print(candle.ts, signal.stop_loss, candle.ma_close, candle.sti_trend)
        elif signal.strategy in ('ST_Buy', 'P_Buy') and signal.status != 'C' and candle.sti_dir == -1:
            signal.stop_loss = round(
                candle.ma_close - self.stoploss_gap, 2)
            signal.ma_stoploss = True
            # print(candle.ts, signal.stop_loss, candle.ma_close)

        if signal.strategy in ('ST_Sell', 'P_Sell') and signal.status != 'C' and candle.sti_dir == -1:
            signal.stop_loss = round(candle.sti_trend + self.stoploss_gap, 2)
            signal.ma_stoploss = False
            if candle.ma_close > candle.sti_trend and abs(candle.ma_close - candle.sti_trend) <= self.supertrend_ma_margin:
                signal.stop_loss = round(
                    candle.ma_close + self.stoploss_gap, 2)
                signal.ma_stoploss = True
            # print(candle.ts, signal.stop_loss, candle.ma_close)
        elif signal.strategy in ('ST_Sell', 'P_Sell') and signal.status != 'C' and candle.sti_dir == 1:
            signal.stop_loss = round(
                candle.ma_close + self.stoploss_gap, 2)
            signal.ma_stoploss = True
            # print(candle.ts, signal.stop_loss, candle.ma_close)

        sti_buy_passed = candle.sti_dir == 1
        sti_sell_passed = candle.sti_dir == -1

        stop_loss_passed = abs(
            candle.close - candle.sti_trend) <= self.stoploss_margin

        buy_stoploss = candle.sti_trend - self.stoploss_gap
        sell_stoploss = candle.sti_trend + self.stoploss_gap

        initial_buy_passed = sti_buy_passed and (
            signal.strategy in ('', 'ST_Sell', 'P_Sell', 'ST_Buy', 'P_Buy'))
        initial_sell_passed = sti_sell_passed and (
            signal.strategy in ('', 'ST_Buy', 'P_Buy', 'ST_Sell', 'P_Sell'))

        # if str(candle.ts).find('2022-01-21 09:') != -1:
        #    print(initial_buy_passed, sti_buy_passed,
        #          initial_sell_passed, sti_sell_passed, signal.status)

        if sti_buy_passed and signal.status in ('X', 'C', 'P'):
            if(buy_ma_passed):
                pbuy_sig = CBSignal(
                    'P_Buy', self.chart.sym, self.chart.lot_size, candle.ts, 0, candle.sti_trend, candle)
                pbuy_sig.status = 'P'
                pbuy_sig.sti_trend = candle.sti_trend
                pbuy_sig.prev_sti_trend = prev_candle.sti_trend
                pbuy_sig.ma_close = candle.ma_close
                return 'PSig', pbuy_sig

        if sti_sell_passed and signal.status in ('X', 'C', 'P'):
            if(sell_ma_passed):
                psell_sig = CBSignal(
                    'P_Sell', self.chart.sym, self.chart.lot_size, candle.ts, 0, candle.sti_trend, candle)
                psell_sig.status = 'P'
                psell_sig.sti_trend = candle.sti_trend
                psell_sig.prev_sti_trend = prev_candle.sti_trend
                psell_sig.ma_close = candle.ma_close

                return 'PSig', psell_sig

        return '', None

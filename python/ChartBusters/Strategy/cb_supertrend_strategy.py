from ChartBusters.Strategy.cb_strategy import CBStrategy
from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_candle import CBCandle
from ChartBusters.Strategy.cb_strategy_result import CBStrategyResult
from ChartBusters.cb_signal import CBSignal
from typing import List, Tuple


class CBSuperTrendStrategy(CBStrategy):
    def __init__(self, strategy: str, chart: CBChart, expiry, rsi: float = 30,
                 close_margin: int = 50, stoploss_margin: int = 120, supertrend_ma_margin: int = 30,
                 stoploss_gap: int = 20, close_ema_margin: int = 350) -> None:
        super().__init__(chart)
        self.strategy = strategy
        self.rsi = rsi
        self.close_margin = close_margin
        self.stoploss_margin = stoploss_margin
        self.stoploss_gap = stoploss_gap
        self.supertrend_ma_margin = supertrend_ma_margin
        self.close_ema_margin = close_ema_margin
        self.stop_gain = 200000000
        self.expiry = expiry
        self.expiry_ts = self.expiry + ' 15:00:00+05:30'
        self.expiry_ts2 = self.expiry + ' 15:15:00+05:30'
        self.expiry_t = ' 15:00:00+05:30'
        self.expiry_t2 = ' 15:15:00+05:30'
        if(self.strategy == 'SuperTrend60'):
            self.expiry_ts = self.expiry + ' 14:15:00+05:30'

    def execute(self, candle: CBCandle, signal: CBSignal) -> Tuple[str, CBSignal]:
        prev_candle = self.chart.previous(candle)
        next_candle = self.chart.get_next_candles(candle.ts, 1)[0]
        rsi = candle.rsi

        stop_loss_updated_ema = False
        if(str(candle.ts) == self.expiry_ts2):
            return '', None

        # Series Expiry Signal Closure
        if(str(candle.ts) == self.expiry_ts):
            if (signal.status == 'O'):
                signal.status = 'C'
                signal.exit_ts = next_candle.ts
                signal.exit_price = next_candle.open
                signal.pnl = round(
                    (signal.entry_price - next_candle.open)*signal.lot_size, 2)
                if signal.strategy == 'ST_Buy':
                    signal.pnl = -1 * signal.pnl
                signal.comment = 'Position squared off at expiry'

                return 'SL', None

        buy_ma_passed = candle.ma_close < candle.low
        sell_ma_passed = candle.ma_close > candle.high

        # Verify potential signals
        if (signal.strategy == 'P_Buy' and candle.sti_dir == 1):
            rsi_passed = rsi > 30
            stop_loss_passed = abs(
                candle.sti_trend - candle.close) <= self.stoploss_margin
            close_margin_passed = abs(
                signal.prev_sti_trend - candle.close) <= self.close_margin

            if(rsi_passed and stop_loss_passed and buy_ma_passed):
                # print('Converting PSig to Buy. TS: {}'.format(candle.ts))
                buy_stoploss = candle.sti_trend - self.stoploss_gap
                buy_signal = CBSignal(
                    'ST_Buy', self.chart.sym, self.chart.lot_size, next_candle.ts, next_candle.open, buy_stoploss, candle)
                buy_signal.sti_trend = round(signal.sti_trend, 2)
                buy_signal.ema_close = round(signal.ema_close, 2)
                return 'New', buy_signal

        if (signal.strategy == 'P_Sell' and candle.sti_dir == -1):
            rsi_passed = rsi < 70
            stop_loss_passed = abs(
                candle.sti_trend - candle.close) <= self.stoploss_margin
            close_margin_passed = abs(
                signal.prev_sti_trend - candle.close) <= self.close_margin

            if(rsi_passed and stop_loss_passed and sell_ma_passed):
                # print('Converting PSig to Sell. TS: {}'.format(candle.ts))
                sell_stoploss = candle.sti_trend + self.stoploss_gap
                sell_signal = CBSignal(
                    'ST_Sell', self.chart.sym, self.chart.lot_size, next_candle.ts, next_candle.open, sell_stoploss, candle)
                sell_signal.sti_trend = round(signal.sti_trend, 2)
                sell_signal.ema_close = round(signal.ema_close, 2)
                return 'New', sell_signal

        # Stop Loss Checks
        if (signal.strategy == 'ST_Buy' and signal.status == 'O'):
            if (abs(candle.high - candle.ema_close) > self.close_ema_margin):
                signal.status = 'C'
                signal.exit_ts = next_candle.ts
                signal.exit_price = next_candle.open
                signal.pnl = round(
                    (next_candle.open - signal.entry_price)*signal.lot_size, 2)
                signal.comment = 'Close EMA diff greater than {}'.format(
                    self.close_ema_margin)

            elif (candle.low < signal.stop_loss):
                signal.status = 'C'
                signal.exit_ts = candle.ts
                signal.exit_price = signal.stop_loss
                signal.comment = 'StopLoss breached'
                if (candle.high < signal.stop_loss):
                    signal.exit_price = candle.open
                    signal.comment = 'StopLoss breached. Gap down opening. PnL Impact: {}'.format(
                        round(abs(candle.open-signal.stop_loss)*signal.lot_size), 2)
                signal.pnl = round(-1 *
                                   (signal.entry_price - signal.exit_price)*signal.lot_size, 2)
                # return 'SL', None

        if (signal.strategy == 'ST_Sell' and signal.status == 'O'):
            if (abs(candle.low - candle.ema_close) > self.close_ema_margin):
                signal.status = 'C'
                signal.exit_ts = next_candle.ts
                signal.exit_price = next_candle.open
                signal.pnl = round((signal.entry_price -
                                    next_candle.open)*signal.lot_size, 2)
                signal.comment = 'Close EMA diff greater than {}'.format(
                    self.close_ema_margin)

            elif(candle.high > signal.stop_loss):
                signal.status = 'C'
                signal.exit_ts = candle.ts
                signal.exit_price = signal.stop_loss
                signal.comment = 'StopLoss breached'
                if (candle.low > signal.stop_loss):
                    signal.exit_price = candle.open
                    signal.comment = 'StopLoss breached. Gap up opening. PnL Impact: {}'.format(
                        round(abs(candle.open-signal.stop_loss)*signal.lot_size), 2)
                signal.pnl = round(-1 *
                                   (signal.exit_price - signal.entry_price)*signal.lot_size, 2)
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
            if candle.ma_close < candle.sti_trend and abs(candle.ma_close - candle.sti_trend) <= self.supertrend_ma_margin:
                # print("Stop loss updated")
                signal.stop_loss = round(
                    candle.ma_close - self.stoploss_gap, 2)
                signal.ema_stoploss = True
        elif signal.strategy in ('ST_Buy', 'P_Buy') and signal.status != 'C' and candle.sti_dir == -1:
            signal.stop_loss = round(
                candle.ma_close, 2)
            signal.ema_stoploss = True

        if signal.strategy in ('ST_Sell', 'P_Sell') and signal.status != 'C' and candle.sti_dir == -1:
            signal.stop_loss = round(candle.sti_trend + self.stoploss_gap, 2)
            if candle.ma_close > candle.sti_trend and abs(candle.ma_close - candle.sti_trend) <= self.supertrend_ma_margin:
                # print("Stop loss updated")
                signal.stop_loss = round(
                    candle.ma_close + self.stoploss_gap, 2)
                signal.ema_stoploss = True
        elif signal.strategy in ('ST_Sell', 'P_Sell') and signal.status != 'C' and candle.sti_dir == 1:
            signal.stop_loss = round(
                candle.ma_close, 2)
            signal.ema_stoploss = True

        buy_rsi_passed = rsi > 30
        sell_rsi_passed = rsi < 70
        close_margin_passed = abs(
            candle.close - prev_candle.sti_trend) <= self.close_margin

        sti_buy_passed = candle.sti_dir == 1
        sti_sell_passed = candle.sti_dir == -1

        stop_loss_passed = abs(
            candle.close - candle.sti_trend) <= self.stoploss_margin

        buy_stoploss = candle.sti_trend - self.stoploss_gap
        sell_stoploss = candle.sti_trend + self.stoploss_gap

        initial_buy_passed = sti_buy_passed and (
            signal.strategy in ('', 'ST_Sell', 'P_Sell'))
        initial_sell_passed = sti_sell_passed and (
            signal.strategy in ('', 'ST_Buy', 'P_Buy'))

        if initial_buy_passed and signal.status in ('X', 'C'):
            if(not buy_rsi_passed or not stop_loss_passed or not buy_ma_passed):
                pbuy_sig = CBSignal(
                    'P_Buy', self.chart.sym, self.chart.lot_size, candle.ts, 0, candle.sti_trend, candle)
                signal.status = 'P'
                pbuy_sig.sti_trend = candle.sti_trend
                pbuy_sig.prev_sti_trend = prev_candle.sti_trend
                pbuy_sig.ema_close = candle.ma_close
                return 'PSig', pbuy_sig
            else:
                buy_signal = CBSignal(
                    'ST_Buy', self.chart.sym, self.chart.lot_size, next_candle.ts, next_candle.open, buy_stoploss, candle)
                buy_signal.sti_trend = round(candle.sti_trend, 2)
                buy_signal.ema_close = round(candle.ma_close, 2)
                return 'New', buy_signal

        if initial_sell_passed and signal.status in ('X', 'C'):
            if(not sell_rsi_passed or not stop_loss_passed or not sell_ma_passed):
                psell_sig = CBSignal(
                    'P_Sell', self.chart.sym, self.chart.lot_size, candle.ts, 0, candle.sti_trend, candle)
                signal.status = 'P'
                psell_sig.sti_trend = candle.sti_trend
                psell_sig.prev_sti_trend = prev_candle.sti_trend
                psell_sig.ema_close = candle.ma_close

                return 'PSig', psell_sig
            else:
                sell_signal = CBSignal(
                    'ST_Sell', self.chart.sym, self.chart.lot_size, next_candle.ts, next_candle.open, sell_stoploss, candle)
                sell_signal.sti_trend = round(candle.sti_trend, 2)
                sell_signal.ema_close = round(candle.ma_close, 2)
                return 'New', sell_signal

        return '', None

from ChartBusters.Strategy.cb_strategy import CBStrategy
from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_candle import CBCandle
from ChartBusters.Strategy.cb_strategy_result import CBStrategyResult
from ChartBusters.cb_signal import CBSignal
from typing import List, Tuple


class CBSuperTrendStrategy(CBStrategy):
    def __init__(self, strategy: str, chart: CBChart, expiry, rsi: float = 30, close_margin: int = 50, stoploss_margin: int = 10) -> None:
        super().__init__(chart)
        self.strategy = strategy
        self.rsi = rsi
        self.close_margin = close_margin
        self.stoploss_margin = stoploss_margin
        self.expiry = expiry
        self.stop_loss = 5000
        self.expiry_ts = self.expiry + ' 15:00:00+05:30'
        if(self.strategy == 'SuperTrend60'):
            self.expiry_ts = self.expiry + ' 14:15:00+05:30'

    def execute(self, candle: CBCandle, signal: CBSignal) -> Tuple[str, CBSignal]:
        prev_candle = self.chart.previous(candle)
        next_candle = self.chart.get_next_candles(candle.ts, 1)[0]
        rsi = candle.rsi

        if(str(candle.ts) == self.expiry_ts):
            signal.status = 'C'
            signal.exit_ts = next_candle.ts
            signal.exit_price = next_candle.open
            signal.pnl = round(
                (signal.entry_price - next_candle.open)*signal.lot_size, 2)
            if signal.strategy == 'ST_Buy':
                signal.pnl = -1 * signal.pnl
            signal.comment = 'Position squared off at expiry'

            return 'SL', None

        # Stop Loss Checks
        if (signal.strategy == 'ST_Buy'):
            if(candle.low < signal.stop_loss):
                signal.status = 'C'
                signal.exit_ts = candle.ts
                signal.exit_price = signal.stop_loss
                signal.pnl = round(-1 *
                                   (signal.entry_price - signal.stop_loss)*signal.lot_size, 2)
                signal.comment = 'StopLoss breached'
                return 'SL', None

        if (signal.strategy == 'ST_Sell'):
            if(candle.high > signal.stop_loss):
                signal.status = 'C'
                signal.exit_ts = candle.ts
                signal.exit_price = signal.stop_loss
                signal.pnl = round(-1 *
                                   (signal.stop_loss - signal.entry_price)*signal.lot_size, 2)
                signal.comment = 'StopLoss breached'
                return 'SL', None

        buy_rsi_passed = rsi > 30
        sell_rsi_passed = rsi < 70
        close_margin_passed = abs(
            candle.close - prev_candle.sti_trend) <= self.close_margin

        sti_buy_passed = candle.sti_dir == 1 and prev_candle.sti_dir == -1
        sti_sell_passed = candle.sti_dir == -1 and prev_candle.sti_dir == 1

        # buy_stoploss = (candle.ema_close if (candle.sti_trend <
        #                candle.ema_close and candle.ema_close < candle.close) else candle.sti_trend) - self.stoploss_margin
        # sell_stoploss = (candle.ema_close if (candle.sti_trend >
        #                 candle.ema_close and candle.ema_close > candle.close) else candle.sti_trend) + self.stoploss_margin
        buy_stoploss = candle.sti_trend - self.stoploss_margin
        sell_stoploss = candle.sti_trend + self.stoploss_margin

        buy_passed = buy_rsi_passed and close_margin_passed and sti_buy_passed and (
            signal.strategy == '' or signal.strategy == 'ST_Sell')
        sell_passed = sell_rsi_passed and close_margin_passed and sti_sell_passed and (
            signal.strategy == '' or signal.strategy == 'ST_Buy')

        if buy_passed:
            if(signal.strategy == 'ST_Sell'):
                signal.status = 'C'
                signal.exit_ts = next_candle.ts
                signal.exit_price = next_candle.open
                signal.pnl = round((signal.entry_price -
                                    next_candle.open)*signal.lot_size, 2)
                signal.comment = 'STI Reversal'

            sl = round(candle.close - self.stop_loss /
                       self.chart.lot_size, 2)
            # buy_stoploss = sl

            buy_signal = CBSignal(
                'ST_Buy', self.chart.sym, self.chart.lot_size, next_candle.ts, next_candle.open, buy_stoploss, candle)
            buy_signal.sti_trend = round(candle.sti_trend, 2)
            buy_signal.ema_close = round(candle.ema_close, 2)
            return 'New', buy_signal

        if sell_passed:
            if(signal.strategy == 'ST_Buy'):
                signal.status = 'C'
                signal.exit_ts = next_candle.ts
                signal.exit_price = next_candle.open
                signal.pnl = round(
                    (next_candle.open - signal.entry_price)*signal.lot_size, 2)
                signal.comment = 'STI Reversal'

            sl = round(candle.close + self.stop_loss /
                       self.chart.lot_size, 2)
            # sell_stoploss = sl

            sell_signal = CBSignal(
                'ST_Sell', self.chart.sym, self.chart.lot_size, next_candle.ts, next_candle.open, sell_stoploss, candle)
            sell_signal.sti_trend = round(candle.sti_trend, 2)
            sell_signal.ema_close = round(candle.ema_close, 2)
            return 'New', sell_signal

        return '', None

    def back_test(self, start_ts, end_ts) -> List[CBSignal]:
        results = list()
        signal = CBSignal('', '', 0, '', 0, 0, None)
        candles = self.chart.sub_chart(start_ts, end_ts)
        for candle in candles:
            sig_type, new_signal = self.execute(candle, signal)
            if (sig_type == 'New'):
                results.append(new_signal)
                signal = new_signal
            if(sig_type == 'SL'):
                signal = CBSignal('', '', 0, '', 0, 0, None)

        return results

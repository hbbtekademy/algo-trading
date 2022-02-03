from ChartBusters.Strategy.cb_strategy import CBStrategy
from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_candle import CBCandle
from ChartBusters.Strategy.cb_strategy_result import CBStrategyResult
from ChartBusters.cb_signal import CBSignal
from typing import List, Tuple


class CBSuperTrendStrategyV1(CBStrategy):
    def __init__(self, chart: CBChart, expiry, rsi: float = 30, close_margin: int = 50, stoploss_margin: int = 10) -> None:
        super().__init__(chart)
        self.strategy = 'SuperTrendV1'
        self.rsi = rsi
        self.close_margin = close_margin
        self.stoploss_margin = stoploss_margin
        self.stop_loss = 2500
        self.expiry = expiry

    def execute(self, candle: CBCandle, signal: CBSignal) -> Tuple[str, CBSignal]:
        prev_candle = self.chart.previous(candle)
        rsi = candle.rsi
        adx = candle.adx

        expiry_ts = self.expiry + ' 15:15:00+05:30'
        if(str(candle.ts) == expiry_ts):
            signal.exit_ts = candle.ts
            signal.exit_price = candle.close
            signal.pnl = round(
                (signal.entry_price - candle.close)*signal.lot_size, 2)
            if signal.strategy == 'ST_Buy':
                signal.pnl = -1 * signal.pnl
            signal.comment = 'Position squared off at expiry'

            return 'SL', None

        # Update Stop Loss
        if signal.strategy == 'ST_Buy' and candle.sti_dir == 1:
            signal.stop_loss = signal.stop_loss
        if signal.strategy == 'ST_Sell' and candle.sti_dir == -1:
            signal.stop_loss = signal.stop_loss

        # Stop Loss Checks
        if (signal.strategy == 'ST_Buy'):
            if(candle.low < signal.stop_loss):
                signal.exit_ts = candle.ts
                signal.exit_price = signal.stop_loss
                signal.pnl = round(-1 *
                                   (signal.entry_price - signal.stop_loss)*signal.lot_size, 2)
                signal.comment = 'StopLoss breached'
                return 'SL', None

        if (signal.strategy == 'ST_Sell'):
            if(candle.high > signal.stop_loss):
                signal.exit_ts = candle.ts
                signal.exit_price = signal.stop_loss
                signal.pnl = round(-1 *
                                   (signal.stop_loss - signal.entry_price)*signal.lot_size, 2)
                signal.comment = 'StopLoss breached'
                return 'SL', None
            pass

        # Buy/Sell signal checks
        sti_buy_passed = candle.sti_dir == 1 and prev_candle.sti_dir == -1
        sti_sell_passed = candle.sti_dir == -1 and prev_candle.sti_dir == 1
        ema_close_buy_passed = candle.close > candle.ema_close
        ema_close_sell_passed = candle.close < candle.ema_close
        #ema_close_buy_passed = True
        #ema_close_sell_passed = True
        adx_passed = adx >= 30
        rsi_buy_passed = rsi >= 70
        rsi_sell_passed = rsi <= 30

        buy_stoploss = (candle.sti_trend if candle.sti_trend >
                        candle.ema_close else candle.ema_close) - self.stoploss_margin
        sell_stoploss = (candle.ema_close if candle.sti_trend >
                         candle.ema_close else candle.sti_trend) + self.stoploss_margin

        buy_passed = ema_close_buy_passed and sti_buy_passed and (
            signal.strategy == '' or signal.strategy == 'ST_Sell')
        sell_passed = ema_close_sell_passed and sti_sell_passed and (
            signal.strategy == '' or signal.strategy == 'ST_Buy')

        if buy_passed:
            if(signal.strategy == 'ST_Sell'):
                signal.exit_ts = candle.ts
                signal.exit_price = candle.close
                signal.pnl = round((signal.entry_price -
                                    candle.close)*signal.lot_size, 2)
                signal.comment = 'STI Reversal'

            stop_loss = round(candle.close - self.stop_loss /
                              self.chart.lot_size, 2)
            #stop_loss = buy_stoploss
            buy_signal = CBSignal(
                'ST_Buy', self.chart.sym, self.chart.lot_size, candle.ts, candle.close, stop_loss, candle)
            return 'New', buy_signal

        if sell_passed:
            if(signal.strategy == 'ST_Buy'):
                signal.exit_ts = candle.ts
                signal.exit_price = candle.close
                signal.pnl = round(
                    (candle.close - signal.entry_price)*signal.lot_size, 2)
                signal.comment = 'STI Reversal'

            stop_loss = round(candle.close + self.stop_loss /
                              self.chart.lot_size, 2)
            #stop_loss = sell_stoploss
            sell_signal = CBSignal(
                'ST_Sell', self.chart.sym, self.chart.lot_size, candle.ts, candle.close, stop_loss, candle)
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

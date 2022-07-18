import copy
from typing import List

from python.chartbusters.model.cb_candle import CBCandle
from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v3 import CBSignalV3
from python.chartbusters.strategies.cb_strategy import CBStrategy


class CBSuperTrendStrategyV3(CBStrategy):
    def __init__(self, strategy: str, chart: CBChart, expiry, rsi: float = 30,
                 close_margin: int = 50, stoploss_margin: int = 120, supertrend_ema_margin: int = 30,
                 stoploss_gap: int = 20, close_ema_margin: int = 350) -> None:
        super().__init__(chart)
        self.strategy = strategy
        self.rsi = rsi
        self.close_margin = close_margin
        self.stoploss_margin = stoploss_margin
        self.stoploss_gap = stoploss_gap
        self.supertrend_ema_margin = supertrend_ema_margin
        self.close_ema_margin = close_ema_margin
        self.expiry = expiry
        self.expiry_ts = self.expiry + ' 15:00:00+05:30'
        if self.strategy == 'SuperTrend60':
            self.expiry_ts = self.expiry + ' 14:15:00+05:30'

    def execute(self, candle: CBCandle, signal: CBSignalV3) -> List[CBSignalV3]:
        signals = list()
        prev_candle = self.chart.previous(candle)
        next_candle = self.chart.get_next_candles(candle.ts, 1)[0]
        rsi = candle.rsi

        stop_loss_updated_ema = False

        # Series Expiry Signal Closure
        if str(candle.ts) == self.expiry_ts:
            strategy = ''
            if signal.strategy == 'ST_Buy':
                strategy = 'ST_Sell'
            else:
                strategy = 'ST_Buy'

            expSignal = CBSignalV3(strategy, signal.sym,
                                   signal.lot_size, candle.ts, 0, candle)
            expSignal.status = 'Expiry'
            expSignal.comment = 'Expiry square off Signal'
            signals.append(expSignal)
            return signals

        # Verify potential signals
        if signal.strategy == 'P_Buy' and candle.sti_dir == 1:
            rsi_passed = rsi > 30
            stop_loss_passed = abs(
                candle.sti_trend - candle.close) <= self.stoploss_margin

            if rsi_passed and stop_loss_passed:
                # print('Converting PSig to rsi. TS: {}'.format(candle.ts))
                buy_stoploss = candle.sti_trend - self.stoploss_gap
                buy_signal = CBSignalV3(
                    'ST_Buy', self.chart.sym, self.chart.lot_size, candle.ts, buy_stoploss, candle)
                signals.append(buy_signal)
                return signals

        if signal.strategy == 'P_Sell' and candle.sti_dir == -1:
            rsi_passed = rsi < 70
            stop_loss_passed = abs(
                candle.sti_trend - candle.close) <= self.stoploss_margin

            if rsi_passed and stop_loss_passed:
                # print('Converting PSig to sell. TS: {}'.format(candle.ts))
                sell_stoploss = candle.sti_trend + self.stoploss_gap
                sell_signal = CBSignalV3(
                    'ST_Sell', self.chart.sym, self.chart.lot_size, candle.ts, sell_stoploss, candle)
                signals.append(sell_signal)
                return signals

        stoploss_breached = False
        # Stop Loss Checks
        if signal.strategy == 'ST_Buy' and signal.status in ('O', 'U'):
            if abs(candle.close - candle.ema_close) > self.close_ema_margin:
                slSignal = CBSignalV3('ST_Sell', self.chart.sym,
                                      self.chart.lot_size, candle.ts, 0, candle)
                slSignal.status = 'SL'
                slSignal.comment = 'Close EMA diff greater than {}'.format(
                    self.close_ema_margin)

                stoploss_breached = True
                signals.append(slSignal)

            elif candle.low < signal.stop_loss:
                slSignal = CBSignalV3('ST_Sell', self.chart.sym,
                                      self.chart.lot_size, candle.ts, 0, candle)
                slSignal.status = 'SL'
                slSignal.comment = 'StopLoss breached'

                stoploss_breached = True
                # signals.append(slSignal)

        if (signal.strategy == 'ST_Sell' and signal.status in ('O', 'U')):
            if (abs(candle.close - candle.ema_close) > self.close_ema_margin):
                slSignal = CBSignalV3('ST_Buy', self.chart.sym,
                                      self.chart.lot_size, candle.ts, 0, candle)
                slSignal.status = 'SL'
                slSignal.comment = 'Close EMA diff greater than {}'.format(
                    self.close_ema_margin)

                stoploss_breached = True
                signals.append(slSignal)

            elif candle.high > signal.stop_loss:
                slSignal = CBSignalV3('ST_Buy', self.chart.sym,
                                      self.chart.lot_size, candle.ts, 0, candle)
                slSignal.status = 'SL'
                slSignal.comment = 'StopLoss breached'

                stoploss_breached = True
                # signals.append(slSignal)

        # Update Stop Loss
        if stoploss_breached is False and signal.strategy in ('ST_Buy', 'P_Buy') and signal.status in (
        'O', 'P', 'U') and candle.sti_dir == 1:
            stop_loss = round(candle.sti_trend - self.stoploss_gap, 2)
            ema_stoploss = False
            if candle.ema_close < candle.sti_trend and abs(
                    candle.ema_close - candle.sti_trend) <= self.supertrend_ema_margin:
                # print("Stop loss updated")
                stop_loss = round(
                    candle.ema_close - self.stoploss_gap, 2)
                ema_stoploss = True

            '''if (candle.is_last_candle() or candle.is_sod_candle()) and candle.ema_close < candle.sti_trend:
                stop_loss = round(
                    candle.ema_close - self.stoploss_gap, 2)
                ema_stoploss = True'''

            if stop_loss != signal.stop_loss:
                updSignal = copy.deepcopy(signal)
                updSignal.stop_loss = stop_loss
                updSignal.status = 'U'
                updSignal.ema_close = ema_stoploss
                signals.append(updSignal)

        if stoploss_breached == False and signal.strategy in ('ST_Sell', 'P_Sell') and signal.status in (
        'O', 'P', 'U') and candle.sti_dir == -1:
            stop_loss = round(candle.sti_trend + self.stoploss_gap, 2)
            ema_stoploss = False
            if candle.ema_close > candle.sti_trend and abs(
                    candle.ema_close - candle.sti_trend) <= self.supertrend_ema_margin:
                # print("Stop loss updated")
                stop_loss = round(
                    candle.ema_close + self.stoploss_gap, 2)
                ema_stoploss = True

            '''if (candle.is_last_candle() or candle.is_sod_candle()) and candle.ema_close > candle.sti_trend:
                stop_loss = round(
                    candle.ema_close + self.stoploss_gap, 2)'''

            if stop_loss != signal.stop_loss:
                updSignal = copy.deepcopy(signal)
                updSignal.stop_loss = stop_loss
                updSignal.status = 'U'
                updSignal.ema_close = ema_stoploss
                signals.append(updSignal)

        buy_rsi_passed = rsi > 30
        sell_rsi_passed = rsi < 70
        close_margin_passed = abs(
            candle.close - prev_candle.sti_trend) <= self.close_margin

        sti_buy_passed = candle.sti_dir == 1 and prev_candle.sti_dir == -1
        sti_sell_passed = candle.sti_dir == -1 and prev_candle.sti_dir == 1

        stop_loss_passed = abs(
            candle.close - candle.sti_trend) <= self.stoploss_margin

        buy_stoploss = candle.sti_trend - self.stoploss_gap
        sell_stoploss = candle.sti_trend + self.stoploss_gap

        initial_buy_passed = sti_buy_passed and (
                signal.strategy in ('', 'ST_Sell', 'P_Sell'))
        initial_sell_passed = sti_sell_passed and (
                signal.strategy in ('', 'ST_Buy', 'P_Buy'))

        if initial_buy_passed:
            if signal.strategy == 'ST_Sell' and signal.status in ('O', 'U'):
                # buy_signal = CBSignal('ST_Buy', self.chart.sym,
                #                      self.chart.lot_size, candle.ts, 0, candle)
                rev_signal = copy.deepcopy(signal)
                rev_signal.status = 'C'
                rev_signal.exit_ts = candle.ts
                rev_signal.comment = 'STI Reversal'
                signals.append(rev_signal)

            if (not buy_rsi_passed or not stop_loss_passed):
                pbuy_sig = CBSignalV3(
                    'P_Buy', self.chart.sym, self.chart.lot_size, candle.ts, 0, candle)
                pbuy_sig.status = 'P'
                signals.append(pbuy_sig)
            else:
                buy_signal = CBSignalV3(
                    'ST_Buy', self.chart.sym, self.chart.lot_size, candle.ts, buy_stoploss, candle)
                signals.append(buy_signal)

        if initial_sell_passed:
            if signal.strategy == 'ST_Buy' and signal.status in ('O', 'U'):
                # sell_signal = CBSignal('ST_Sell', self.chart.sym,
                #                       self.chart.lot_size, candle.ts, 0, candle)
                rev_signal = copy.deepcopy(signal)
                rev_signal.status = 'C'
                rev_signal.exit_ts = candle.ts
                rev_signal.comment = 'STI Reversal'
                signals.append(rev_signal)

            if not sell_rsi_passed or not stop_loss_passed:
                psell_sig = CBSignalV3(
                    'P_Sell', self.chart.sym, self.chart.lot_size, candle.ts, 0, candle)
                psell_sig.status = 'P'
                signals.append(psell_sig)
            else:
                sell_signal = CBSignalV3(
                    'ST_Sell', self.chart.sym, self.chart.lot_size, candle.ts, sell_stoploss, candle)
                signals.append(sell_signal)

        return signals

    def back_test(self, start_ts, end_ts):
        curr_signal = CBSignalV3('', '', 0, '', 0, None)
        backtest_signals = list()
        candles = self.chart.sub_chart(start_ts, end_ts)

        for candle in candles:
            prev_candle = self.chart.previous(candle)
            if curr_signal.strategy in ('ST_Buy', 'ST_Sell'):
                if curr_signal.strategy == 'ST_Buy' and candle.low < curr_signal.stop_loss:
                    curr_signal.comment = 'Stoploss breached'
                    curr_signal.status = 'C'
                    curr_signal.exit_ts = candle.ts
                    curr_signal = CBSignalV3('', '', 0, '', 0, None)
                if curr_signal.strategy == 'ST_Sell' and candle.high > curr_signal.stop_loss:
                    curr_signal.comment = 'Stoploss breached'
                    curr_signal.status = 'C'
                    curr_signal.exit_ts = candle.ts
                    curr_signal = CBSignalV3('', '', 0, '', 0, None)

            signals = self.execute(candle, curr_signal)
            for signal in signals:
                if signal.status in ('O', 'P', 'U'):
                    curr_signal = signal
                    break

            for signal in signals:
                if signal.strategy in ('ST_Buy', 'ST_Sell'):
                    backtest_signals.append(signal)

        for signal in backtest_signals:
            signal.pretty_print()
            pass

from ChartBusters.Strategy.cb_strategy import CBStrategy
from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_candle import CBCandle
from ChartBusters.Strategy.cb_strategy_result import CBStrategyResult
from ChartBusters.cb_signal import CBSignal
from typing import List, Tuple


class CBSuperTrendStrategy(CBStrategy):
    def __init__(self, strategy: str, chart: CBChart, expiry, rsi: float = 30, close_margin: int = 50, stoploss_margin: int = 120) -> None:
        super().__init__(chart)
        self.strategy = strategy
        self.rsi = rsi
        self.close_margin = close_margin
        self.stoploss_margin = stoploss_margin
        self.expiry = expiry
        self.expiry_ts = self.expiry + ' 15:00:00+05:30'
        if(self.strategy == 'SuperTrend60'):
            self.expiry_ts = self.expiry + ' 14:15:00+05:30'

    def execute(self, candle: CBCandle, signal: CBSignal) -> Tuple[str, CBSignal]:
        prev_candle = self.chart.previous(candle)
        next_candle = self.chart.get_next_candles(candle.ts, 1)[0]
        rsi = candle.rsi

        # Series Expiry Signal Closure
        if(str(candle.ts) == self.expiry_ts and signal.status == 'O'):
            signal.status = 'C'
            signal.exit_ts = next_candle.ts
            signal.exit_price = next_candle.open
            signal.pnl = round(
                (signal.entry_price - next_candle.open)*signal.lot_size, 2)
            if signal.strategy == 'ST_Buy':
                signal.pnl = -1 * signal.pnl
            signal.comment = 'Position squared off at expiry'

            return 'SL', None

        # Verify potential signals
        if (signal.strategy == 'P_Buy' and candle.sti_dir == 1):
            rsi_passed = rsi > 30
            stop_loss_passed = abs(
                signal.sti_trend - candle.close) <= self.stoploss_margin
            close_margin_passed = abs(
                signal.prev_sti_trend - candle.close) <= self.close_margin

            if(self.strategy == 'SuperTrend15'):
                # print('PBuy TS:{},SL:{},'.format(
                #    candle.ts, abs(signal.sti_trend - candle.close)))
                pass

            if(rsi_passed and stop_loss_passed):
                # print('Converting PSig to Buy. TS: {}'.format(candle.ts))
                buy_stoploss = signal.sti_trend - 10
                buy_signal = CBSignal(
                    'ST_Buy', self.chart.sym, self.chart.lot_size, next_candle.ts, next_candle.open, buy_stoploss, candle)
                buy_signal.sti_trend = round(signal.sti_trend, 2)
                buy_signal.ema_close = round(signal.ema_close, 2)
                return 'New', buy_signal

        if (signal.strategy == 'P_Sell' and candle.sti_dir == -1):
            rsi_passed = rsi < 70
            stop_loss_passed = abs(
                signal.sti_trend - candle.close) <= self.stoploss_margin
            close_margin_passed = abs(
                signal.prev_sti_trend - candle.close) <= self.close_margin

            if(self.strategy == 'SuperTrend15'):
                # print('PSell TS:{},SL:{},'.format(
                #    candle.ts, abs(signal.sti_trend - candle.close)))
                pass

            if(rsi_passed and stop_loss_passed):
                # print('Converting PSig to Sell. TS: {}'.format(candle.ts))
                sell_stoploss = signal.sti_trend + 10
                sell_signal = CBSignal(
                    'ST_Sell', self.chart.sym, self.chart.lot_size, next_candle.ts, next_candle.open, sell_stoploss, candle)
                sell_signal.sti_trend = round(signal.sti_trend, 2)
                sell_signal.ema_close = round(signal.ema_close, 2)
                return 'New', sell_signal

        # Update Stop Loss
        if signal.strategy == 'ST_Buy' and candle.sti_dir == 1:
            # signal.stop_loss = candle.sti_trend - 10
            pass
        if signal.strategy == 'ST_Sell' and candle.sti_dir == -1:
            # signal.stop_loss = candle.sti_trend + 10
            pass

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

        stop_loss_passed = abs(
            candle.close - candle.sti_trend) <= self.stoploss_margin

        buy_stoploss = candle.sti_trend - 10
        sell_stoploss = candle.sti_trend + 10

        initial_buy_passed = sti_buy_passed and (
            signal.strategy in ('', 'ST_Sell', 'P_Sell'))
        initial_sell_passed = sti_sell_passed and (
            signal.strategy in ('', 'ST_Buy', 'P_Buy'))

        if initial_buy_passed:
            if(signal.strategy == 'ST_Sell'):
                signal.status = 'C'
                signal.exit_ts = next_candle.ts
                signal.exit_price = next_candle.open
                signal.pnl = round((signal.entry_price -
                                    next_candle.open)*signal.lot_size, 2)
                signal.comment = 'STI Reversal'

            # sl = round(candle.close - self.stop_loss /
            #           self.chart.lot_size, 2)
            # buy_stoploss = sl

            if(not buy_rsi_passed or not close_margin_passed or not stop_loss_passed):
                pbuy_sig = CBSignal(
                    'P_Buy', self.chart.sym, self.chart.lot_size, candle.ts, 0, candle.sti_trend, candle)
                signal.status = 'P'
                pbuy_sig.sti_trend = candle.sti_trend
                pbuy_sig.prev_sti_trend = prev_candle.sti_trend
                pbuy_sig.ema_close = candle.ema_close
                return 'PSig', pbuy_sig
            else:
                buy_signal = CBSignal(
                    'ST_Buy', self.chart.sym, self.chart.lot_size, next_candle.ts, next_candle.open, buy_stoploss, candle)
                buy_signal.sti_trend = round(candle.sti_trend, 2)
                buy_signal.ema_close = round(candle.ema_close, 2)
                return 'New', buy_signal

        if initial_sell_passed:
            if(signal.strategy == 'ST_Buy'):
                signal.status = 'C'
                signal.exit_ts = next_candle.ts
                signal.exit_price = next_candle.open
                signal.pnl = round(
                    (next_candle.open - signal.entry_price)*signal.lot_size, 2)
                signal.comment = 'STI Reversal'

            # sl = round(candle.close + self.stop_loss /
            #           self.chart.lot_size, 2)
            # sell_stoploss = sl

            if(not sell_rsi_passed or not close_margin_passed or not stop_loss_passed):
                pbuy_sig = CBSignal(
                    'P_Sell', self.chart.sym, self.chart.lot_size, candle.ts, 0, candle.sti_trend, candle)
                signal.status = 'P'
                pbuy_sig.sti_trend = candle.sti_trend
                pbuy_sig.prev_sti_trend = prev_candle.sti_trend
                pbuy_sig.ema_close = candle.ema_close
                return 'PSig', pbuy_sig
            else:
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

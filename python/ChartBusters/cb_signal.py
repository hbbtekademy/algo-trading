from datetime import date
from ChartBusters.cb_candle import CBCandle


class CBSignal():
    def __init__(self, strategy: str, sym: str, lot_size: int, ts: date, entry_price: float, stop_loss: float,
                 candle: CBCandle) -> None:
        self.status = 'O'
        self.strategy = strategy
        self.sym = sym
        self.lot_size = lot_size
        self.ts = ts
        self.exit_ts = ts
        self.entry_price = round(entry_price, 2)
        self.exit_price = 0
        self.stop_loss = round(stop_loss, 2)
        self.candle = candle
        self.pnl = 0
        self.cost = self.entry_price * self.lot_size
        self.comment = ""

        # For SuperTrend strategy
        self.sti_trend = 0
        self.prev_sti_trend = 0
        self.sti_ma_diff = 0
        self.ma_close = 0
        self.ma_stoploss = False

    def __str__(self) -> str:
        return "Strategy,{},Sym,{},TS,{},Exit TS,{},Entry,{},Exit,{},StopLoss,{},Lot Size,{},PnL,{},Comment,{}".format(
            self.strategy, self.sym, self.ts, self.exit_ts, self.entry_price, -1*self.exit_price,
            self.stop_loss, self.lot_size, round(self.pnl, 2), self.comment)

    def pretty_print(self) -> None:
        print("{},{},{},{},{},{},{},{},{},{},{},{}".format(
            self.strategy, self.sym, self.ts, self.exit_ts, self.entry_price,
            round(self.exit_price,
                  2), self.stop_loss, self.sti_ma_diff, self.ma_stoploss,
            self.lot_size, round(self.pnl, 2), self.comment))

    def is_eod_signal(self) -> bool:
        if str(self.ts).find(' 14:45:00+05:30') != -1:
            return False
        if str(self.ts).find(' 15:00:00+05:30') != -1:
            return False
        if str(self.ts).find(' 15:15:00+05:30') != -1:
            return False

        return False

    @staticmethod
    def print_header() -> None:
        print("Strategy,Sym,TS,Exit TS,Entry,Exit,StopLoss,ST MA Diff,MA StopLoss,Lot Size,PnL,Comment")

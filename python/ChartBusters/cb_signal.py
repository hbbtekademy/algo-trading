from datetime import date
from ChartBusters.cb_candle import CBCandle


class CBSignal():
    def __init__(self, strategy: str, sym: str, lot_size: int, ts: date, entry_price: float, stop_loss: float,
                 candle: CBCandle) -> None:
        self.strategy = strategy
        self.sym = sym
        self.lot_size = lot_size
        self.ts = ts
        self.exit_ts = ts
        self.entry_price = entry_price
        self.exit_price = 0
        self.stop_loss = stop_loss
        self.candle = candle
        self.pnl = 0
        self.cost = self.entry_price * self.lot_size
        self.comment = ""

    def __str__(self) -> str:
        return "Strategy,{},Sym,{},TS,{},Exit TS,{},Entry,{},Exit,{},StopLoss,{},Lot Size,{},PnL,{},Comment,{}".format(
            self.strategy, self.sym, self.ts, self.exit_ts, self.entry_price, -1*self.exit_price,
            self.stop_loss, self.lot_size, round(self.pnl, 2), self.comment)

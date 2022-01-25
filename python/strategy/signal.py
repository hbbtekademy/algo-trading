
from datetime import date


class Signal():
    def __init__(self, strategy: str, sym: str, lot_size: int, ts: date, entry_price: float, stop_loss: float,
                 rsi: float, hourly_rsi: float, vol: int, mean_vol: int, daily_mov_pct: float) -> None:
        self.strategy = strategy
        self.sym = sym
        self.lot_size = lot_size
        self.ts = ts
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.rsi = rsi
        self.hourly_rsi = hourly_rsi
        self.vol = vol
        self.mean_vol = mean_vol
        self.daily_mov_pct = daily_mov_pct
        self.pnl = 0
        self.comment = ""

    def __str__(self) -> str:
        return "Strategy: {}, Sym: {}, TS: {}, Entry: {}, StopLoss: {}, PnL: {}, Comment: {}".format(
            self.strategy, self.sym, self.ts, self.entry_price, self.stop_loss, self.pnl, self.comment)

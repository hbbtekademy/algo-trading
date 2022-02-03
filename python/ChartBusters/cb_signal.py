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

    def __str__(self) -> str:
        return "Strategy,{},Sym,{},TS,{},Exit TS,{},Entry,{},Exit,{},StopLoss,{},Lot Size,{},PnL,{},Comment,{}".format(
            self.strategy, self.sym, self.ts, self.exit_ts, self.entry_price, -1*self.exit_price,
            self.stop_loss, self.lot_size, round(self.pnl, 2), self.comment)

    def pretty_print(self) -> None:
        print("{},{},{},{},{},{},{},{},{},{}".format(
            self.strategy, self.sym, self.ts, self.exit_ts, self.entry_price,
            round(self.exit_price, 2), self.stop_loss, self.lot_size, round(self.pnl, 2), self.comment))

    @staticmethod
    def print_header() -> None:
        print("Strategy,Sym,TS,Exit TS,Entry,Exit,StopLoss,Lot Size,PnL,Comment")

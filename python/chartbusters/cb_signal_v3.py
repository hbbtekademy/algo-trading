from datetime import date

from python.chartbusters.cb_candle import CBCandle


class CBSignal:
    def __init__(self, strategy: str, sym: str, lot_size: int, ts: date, stop_loss: float,
                 candle: CBCandle) -> None:
        self.id = sym + '-' + str(ts)
        self.status = 'O'
        self.strategy = strategy
        self.sym = sym
        self.lot_size = lot_size
        self.ts = ts
        self.stop_loss = round(stop_loss, 2)
        self.candle = candle
        self.comment = ""

        # For SuperTrend strategy
        self.sti_trend = 0
        self.prev_sti_trend = 0
        self.ema_close = 0
        self.ema_stoploss = False

        # Position details for back testing
        self.entry_price = 0
        self.exit_price = 0
        self.entry_ts = None
        self.exit_ts = None
        self.pnl = 0

    def __str__(self) -> str:
        return "strategy,{},Sym,{},TS,{},Exit TS,{},Entry,{},Exit,{},StopLoss,{},Lot Size,{},PnL,{},Comment,{}".format(
            self.strategy, self.sym, self.ts, self.exit_ts, self.entry_price, -1*self.exit_price,
            self.stop_loss, self.lot_size, round(self.pnl, 2), self.comment)

    def pretty_print(self) -> None:
        print("{},{},{},{},{},{},{},{},{},{},{},{}".format(
            self.id, self.status, self.strategy, self.sym, self.ts, self.exit_ts, self.entry_price,
            round(self.exit_price, 2), self.stop_loss,
            self.lot_size, round(self.pnl, 2), self.comment))

    @staticmethod
    def print_header() -> None:
        print("ID,Status,strategy,Sym,TS,Exit TS,Entry,Exit,StopLoss,Lot Size,PnL,Comment")

class BackTestResult():
    def __init__(self, sym: str, signals: list) -> None:
        self.signals = signals
        self.sym = sym
        self.total_pnl = self._calc_total_pnl()
        self.gross_profit = self._calc_gross_profit()
        self.gross_loss = self._calc_gross_loss()
        self.profit_factor = self._calc_profit_factor()

    def _calc_profit_factor(self) -> float:
        gross_profit = self._calc_gross_profit()
        gross_loss = abs(self._calc_gross_loss())
        if (gross_loss == 0):
            gross_loss = 0.1

        profit_factor = gross_profit/gross_loss
        return round(profit_factor, 2)

    def _calc_gross_profit(self) -> float:
        gross_profit = 0
        for signal in self.signals:
            if (signal.pnl > 0):
                gross_profit = gross_profit + signal.pnl

        return round(gross_profit, 2)

    def _calc_gross_loss(self) -> float:
        gross_loss = 0
        for signal in self.signals:
            if (signal.pnl < 0):
                gross_loss = gross_loss - signal.pnl

        return round(gross_loss, 2)

    def _calc_strike_rate(self) -> float:
        if (len(self.signals) == 0):
            return 0

        profit = 0
        notional = 0
        for signal in self.signals:
            if (signal.pnl > 0):
                profit = profit+signal.pnl

            notional = notional + abs(signal.pnl)

        return round(profit/notional, 2)

    def _calc_total_pnl(self) -> float:
        total_pnl = 0
        for signal in self.signals:
            total_pnl = total_pnl + signal.pnl

        return round(total_pnl, 2)

    def __str__(self) -> str:
        return 'Sym,{},Total PnL,{},ProfitFactor,{},GrossProfit,{},GrossLoss,{},Total Signals,{}'.format(
            self.sym, self.total_pnl, self.profit_factor, self.gross_profit, self.gross_loss, len(self.signals))

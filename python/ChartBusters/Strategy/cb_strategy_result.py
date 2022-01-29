
class CBStrategyResult():
    def __init__(self, passed: bool, entry_price: float, stop_loss: float) -> None:
        self.passed = passed
        self.entry_price = entry_price
        self.stop_loss = stop_loss

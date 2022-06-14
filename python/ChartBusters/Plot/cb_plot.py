from ChartBusters.cb_chart import CBChart
from ChartBusters.cb_signal import CBSignal


class CBPlot:
    def __init__(self, chart: CBChart) -> None:
        self.chart = chart

    def plot(self, start_ts, end_ts):
        pass

    def plot_signal(self, signal: CBSignal):
        pass

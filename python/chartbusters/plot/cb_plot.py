from python.chartbusters.cb_chart import CBChart
from python.chartbusters.cb_signal import CBSignal

#why do we need this class ?
class CBPlot:
    def __init__(self, chart: CBChart) -> None:
        self.chart = chart

    def plot(self, start_ts, end_ts):
        pass

    def plot_signal(self, signal: CBSignal):
        pass

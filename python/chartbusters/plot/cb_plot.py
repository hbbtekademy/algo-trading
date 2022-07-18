from python.chartbusters.model.cb_chart import CBChart
from python.chartbusters.model.cb_signal_v1 import CBSignalV1


# why do we need this class ?
class CBPlot:
    def __init__(self, chart: CBChart) -> None:
        self.chart = chart

    def plot(self, start_ts, end_ts):
        pass

    def plot_signal(self, signal: CBSignalV1):
        pass

import plotly.graph_objects as go
import plotly.offline as py
from plotly.subplots import make_subplots

from python.chartbusters.model.cb_chart import CBChart
# We're doing this to provide visual verification mechanism to Sameer?
from python.chartbusters.plot.cb_plot import CBPlot
from python.chartbusters.util import constants


class CBSuperTrendPlot(CBPlot):
    def __init__(self, chart: CBChart) -> None:
        super().__init__(chart)

    def plot(self, start_ts, end_ts):
        candles = self.chart.df[start_ts:end_ts].copy(deep=True)
        candles['DateStr'] = candles.index.strftime('%d-%m %H:%M')

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=('OHLC', 'MACD'),
                            vertical_spacing=0.1,
                            horizontal_spacing=0.01,
                            row_heights=[0.75, 0.25],
                            specs=[[{"secondary_y": False, "type": "candlestick"}],
                                   [{}]])

        # Candlesticks
        fig.add_trace(go.Candlestick(x=candles['DateStr'],
                                     open=candles['Open'],
                                     high=candles['High'],
                                     low=candles['Low'],
                                     close=candles['Close'],
                                     name='Signal Chart',
                                     increasing_line_color='yellow',
                                     increasing_fillcolor='yellow',
                                     decreasing_line_color='red',
                                     decreasing_fillcolor='red',
                                     hoverinfo='skip'),
                      row=1, col=1)

        if self.chart.MA == constants.EMA:
            # EMA Close
            fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.EMA_CLOSE], name='EMA Close',
                                     marker_color='Blue'),
                          row=1, col=1)
        elif self.chart.MA == constants.SMA:
            # SMA Close
            fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.SMA_CLOSE], name='SMA Close',
                                     marker_color='Blue'),
                          row=1, col=1)

            # SuperTrend
        fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.STI_TREND], name='SuperTrend',
                                 marker_color='Cyan'),
                      row=1, col=1)

        # Open
        fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.OPEN], name='Open',
                                 marker_color='Black', mode='markers', marker=dict(size=0.5)),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.HIGH], name='High',
                                 marker_color='Black', mode='markers', marker=dict(size=0.5)),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.LOW], name='Low',
                                 marker_color='Black', mode='markers', marker=dict(size=0.5)),
                      row=1, col=1)
        # Close
        fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.CLOSE], name='Close',
                                 marker_color='Yellow'),
                      row=1, col=1)

        # MACD Line
        fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.MACD], name='MACD',
                                 marker_color='Blue'),
                      row=2, col=1)

        # MACD Signal
        fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.MACD_SIG], name='MACD Signal',
                                 marker_color='Green'),
                      row=2, col=1)

        fig.update_xaxes(type='category', rangeslider=dict(visible=False))
        fig.update_xaxes(showgrid=False, nticks=5)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(xaxis='x')
        fig.update_layout(
            title='SuperTrend strategy Chart',
            title_x=0.5,
            autosize=True,
            hovermode='x unified',
            # width=1450,
            # height=650,
            plot_bgcolor='rgb(5,5,5)',
            paper_bgcolor='rgb(0,0,0)',
            font_color='white')

        py.iplot(fig)

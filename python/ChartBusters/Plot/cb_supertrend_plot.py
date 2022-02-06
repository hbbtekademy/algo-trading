from ChartBusters.Plot.cb_plot import CBPlot
from ChartBusters.cb_chart import CBChart
from ChartBusters import constants
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as py


class CBSuperTrendPlot(CBPlot):
    def __init__(self, chart: CBChart) -> None:
        super().__init__(chart)

    def plot(self, start_ts, end_ts):
        candles = self.chart.df[start_ts:end_ts].copy(deep=True)
        candles['DateStr'] = candles.index.strftime('%d-%m %H:%M')

        fig = make_subplots(rows=1, cols=1, shared_xaxes=False,
                            subplot_titles=('OHLC', ''),
                            vertical_spacing=0.1,
                            horizontal_spacing=0.01,
                            specs=[[{"secondary_y": False, "type": "candlestick"}]])

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
                                     decreasing_fillcolor='red',),
                      row=1, col=1)

        # EMA Close
        fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.EMA_CLOSE], name='EMA Close',
                                 marker_color='Blue'),
                      row=1, col=1)

        # Close
        fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.CLOSE], name='Close',
                                 marker_color='Yellow'),
                      row=1, col=1)

        # SuperTrend
        fig.add_trace(go.Scatter(x=candles['DateStr'], y=candles[constants.STI_TREND], name='SuperTrend',
                                 marker_color='Cyan'),
                      row=1, col=1)

        fig.update_xaxes(type='category', rangeslider=dict(visible=False))
        fig.update_xaxes(showgrid=False, nticks=5)
        fig.update_yaxes(showgrid=False)
        fig.update_layout(
            title='SuperTrend Strategy Chart',
            title_x=0.5,
            autosize=True,
            # width=1450,
            # height=650,
            plot_bgcolor='rgb(5,5,5)',
            paper_bgcolor='rgb(0,0,0)',
            font_color='white')

        py.iplot(fig)

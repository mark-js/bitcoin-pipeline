from typing import List

from plotly.graph_objects import Candlestick, Bar, Figure
from plotly.subplots import make_subplots


def make_candlestick_subplot(candlestick_traces: List[Candlestick], bar_traces: List[Bar]) -> Figure:
    fig = make_subplots(rows=2, cols=1, row_heights=[0.80, 0.20], vertical_spacing=0, shared_xaxes=True)

    for trace in candlestick_traces:
        trace['increasing'] = {'fillcolor':'#3D9970', 'line':{'color':'#3D9970'}}
        trace['decreasing'] = {'fillcolor':'#FF4136', 'line':{'color':'#FF4136'}}
        fig.add_trace(
            trace=trace,
            row=1, col=1
        )
    for trace in bar_traces:
        trace['marker_color'] = 'skyblue'
        fig.add_trace(
            trace=trace,
            row=2, col=1
        )

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        showlegend=False,
        margin={'t':25, 'l':25, 'b':25, 'r':25},
        plot_bgcolor='white',
        paper_bgcolor='white',
        barmode='overlay',
        font_family='monospace')
    fig.update_yaxes(
        row=1, side='right', gridcolor='gainsboro', tickformat='.1f')
    fig.update_xaxes(
        row=1, showline=True, gridcolor='gainsboro')
    fig.update_yaxes(
        row=2, showticklabels=False, showgrid=False)
    fig.update_xaxes(
        row=2, showgrid=False)
    return fig
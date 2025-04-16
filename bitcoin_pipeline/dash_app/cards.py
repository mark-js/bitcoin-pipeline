from dash import html, dcc
from dash.dash_table import DataTable
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc


live_graph_card = dbc.Card(
    dbc.CardBody(
        [
            dcc.Graph(id='live-graph', style={'height':'31rem'}),
            html.P('Last hour', style={'font-size':'0.75rem', 'font-family':'monospace'}),
            dcc.Interval(
                id='live-graph-interval-component',
                interval=200,
                n_intervals=0
            )
        ]
    ),
    style={'height':'34rem'}
)


live_table_card = dbc.Card(
    dbc.CardBody(
        [
            DataTable(
                id='live-table', 
                columns=[
                    {
                        'id':'price',
                        'name':'Price',
                        'type':'numeric',
                        'format':Format(precision=1, scheme=Scheme.fixed)
                    },
                    {
                        'id':'volume',
                        'name':'Volume',
                        'type':'numeric',
                        'format':Format(precision=3, scheme=Scheme.fixed)
                    },
                    {
                        'id':'timestamp',
                        'name':'Time UTC',
                        'type': 'text'
                    }
                ],
                editable=False,
                style_cell={
                    'textAlign':'center',
                    'font-family':'monospace'
                },
                style_table={'overflowX':'scroll'},
                style_data_conditional=[
                    {
                        'if':{
                            'filter_query':'{direction} = Buy',
                            'column_id':['price']
                        },
                        'color':'#3D9970'
                    },
                    {
                        'if':{
                            'filter_query':'{direction} = Sell',
                            'column_id':['price']
                        },
                        'color':'#FF4136'
                    }
                ],
                style_cell_conditional=[
                    {'if': {'column_id':'price'},
                    'width': '27%'},
                    {'if': {'column_id':'volume'},
                    'width': '27%'}
                ]
            ),
            html.P('Last 15 trades', style={'font-size':'0.75rem', 'font-family':'monospace'}),
            dcc.Interval(
                id='live-table-interval-component',
                interval=200,
                n_intervals=0
            )
        ]
    ),
    style={'height':'34rem'}
)


historic_graph_card = dbc.Card(
    dbc.CardBody(
        [
            dbc.RadioItems(
                options=[
                    {'label':'1 min', 'value':1},
                    {'label':'5 min', 'value':5},
                    {'label':'10 min', 'value':10},
                    {'label':'15 min', 'value':15},
                    {'label':'30 min', 'value':30},
                    {'label':'60 min', 'value':60}],
                value=1,
                inline=True,
                id='historical-selection',
                style={'font-family':'monospace', 'padding':'1rem'}
            ),
            dcc.Graph(id='historical-graph', style={'height':'75vh'}),
            html.P('Last 240 time intervals', style={'font-size':'0.75rem', 'font-family':'monospace'})
        ]
    )
)
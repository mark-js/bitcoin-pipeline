from dash import html
import dash_bootstrap_components as dbc
from bitcoin_pipeline.dash_app.cards import live_graph_card, live_table_card, historic_graph_card


layout = dbc.Container(
    dbc.Stack(
        [
            html.H4(
                'Live Data',
                style={
                        'font-family':'monospace',
                        'font-weight':'bold',
                        'padding-top':'2rem'
                }
            ),
            dbc.Row(
                [
                    dbc.Col(
                        live_graph_card,
                        width=9
                    ),
                    dbc.Col(
                        live_table_card,
                        width=3
                    )
                ],
                align='center'
            ),
            html.H4(
                'Historical Data',
                style={
                    'font-family':'monospace',
                    'font-weight':'bold',
                    'padding-top':'2rem'
                }
            ),
            dbc.Row(
                dbc.Col(
                    historic_graph_card
                ),
                align='center',
                style={'padding-bottom':'2rem'}
            )
        ],
        gap=2
    )
)
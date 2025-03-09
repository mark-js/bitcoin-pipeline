from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')
data = df.to_dict('records')

app = Dash(__name__)

app.layout = html.Div([
    html.Div(children='Hello World'),
    html.Hr(),
    dcc.RadioItems(options=['pop', 'lifeExp', 'gdpPercap'], value='pop', id='controls-and-radio-item'),
    dash_table.DataTable(data=data, page_size=10),
    dcc.Graph(figure={}, id='controls-and-graph')
])

@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    return px.histogram(df, x='country', y=col_chosen, histfunc='avg')

app.run(debug=True)
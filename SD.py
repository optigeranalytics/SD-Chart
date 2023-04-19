import yfinance as yf
import pandas as pd
import numpy as np
import dash
from dash import dcc
from dash import html

import plotly.express as px

# Create a Plotly Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Historical Price Data'),

    dcc.Input(id='input-box', type='text', value='NSEBANK'),

    dcc.Graph(
        id='stock-graph',
    )
])


# Define the callback to update the graph when the input value changes
@app.callback(
    dash.dependencies.Output('stock-graph', 'figure'),
    [dash.dependencies.Input('input-box', 'value')])
def update_graph(stock):
    # Fetch the historical price data for the specified stock using yfinance for the past 52 weeks
    stock_data = yf.Ticker(stock)
    stock_data = stock_data.history(period="1y")

    # Calculate the logarithmic returns
    log_returns = np.log(stock_data['Close']).diff()

    # Calculate the mean and standard deviation of the logarithmic returns for the past 52 weeks
    mean = log_returns.tail(52).mean()
    sd = log_returns.tail(52).std()

    # Calculate the upper and lower limits for the ranges with +1SD and -1SD
    upper_limit = stock_data['Close'].tail(1).iloc[0] * np.exp(mean + sd)
    lower_limit = stock_data['Close'].tail(1).iloc[0] * np.exp(mean - sd)

    # Define the data and layout of the graph
    data = [
        {'x': stock_data.index, 'y': stock_data['Close'], 'type': 'line', 'name': 'Price'},
        {'x': stock_data.index, 'y': [upper_limit] * len(stock_data.index), 'type': 'line', 'name': 'Upper Limit'},
        {'x': stock_data.index, 'y': [lower_limit] * len(stock_data.index), 'type': 'line', 'name': 'Lower Limit'}
    ]
    layout = {
        'title': f'{stock} Historical Price Data',
        'xaxis': {'title': 'Date'},
        'yaxis': {'title': 'Price'}
    }

    return {'data': data, 'layout': layout}


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

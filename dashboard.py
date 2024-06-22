import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load the data
file_path = 'clean_amazon_sales_report.csv'  # Update this path if necessary
data = pd.read_csv(file_path)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Sales Dashboard"),
    dcc.Tabs([
        dcc.Tab(label='Overview', children=[
            dcc.Graph(id='state-sales-chart'),
            dcc.Graph(id='sales-time-series')
        ])
    ])
])

# Callback to update sales by state chart
@app.callback(
    Output('state-sales-chart', 'figure'),
    Input('state-sales-chart', 'id')
)
def update_state_sales_chart(_):
    sales_by_state = data.groupby('ship-state')['Amount'].sum().reset_index()
    fig = px.bar(sales_by_state, x='ship-state', y='Amount',
                 title='Sales by State',
                 labels={'ship-state': 'State', 'Amount': 'Total Sales'},
                 color='Amount',
                 color_continuous_scale='Viridis')
    return fig

# Callback to update sales trends over time chart
@app.callback(
    Output('sales-time-series', 'figure'),
    Input('sales-time-series', 'id')
)
def update_time_series(_):
    sales_over_time = data.groupby('Date')['Amount'].sum().reset_index()
    fig = px.line(sales_over_time, x='Date', y='Amount',
                  title='Sales Trends Over Time',
                  labels={'Date': 'Date', 'Amount': 'Total Sales'},
                  line_shape='linear')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

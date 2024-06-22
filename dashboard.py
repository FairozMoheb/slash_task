# file_path = 'clean_amazon_sales_report.csv' 
# data = pd.read_csv(file_path)
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# Load the data
file_path = 'clean_amazon_sales_report.csv'  # Update this path if necessary
data = pd.read_csv(file_path)

# Ensure the 'Date' column is in datetime format
data['Date'] = pd.to_datetime(data['Date'])

# Extract month and year from the Date
data['Year'] = data['Date'].dt.year
data['Month'] = data['Date'].dt.month

# Create a column to identify promotional sales
data['Promotion Applied'] = ~data['promotion-ids'].isna()

# Initialize the Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Amazon sales report Dashboard"),
    dcc.Tabs([
        dcc.Tab(label='Sales by State', children=[
            dcc.Graph(id='state-sales-chart')
        ]),
        dcc.Tab(label='Sales Trends Over Time', children=[
            dcc.Graph(id='sales-time-series')
        ]),
        dcc.Tab(label='Monthly Sales Comparison', children=[
            dcc.Graph(id='monthly-sales-chart')
        ]),
        dcc.Tab(label='Top-Selling Products', children=[
            dcc.Graph(id='top-products-chart')
        ]),
        dcc.Tab(label='Top-Selling Categories', children=[
            dcc.Graph(id='top-categories-chart')
        ]),
        dcc.Tab(label='Impact of Promotions on Sales', children=[
            dcc.Graph(id='promotion-impact-chart')
        ]),
        dcc.Tab(label='Sales by Fulfillment Channel', children=[
            dcc.Graph(id='fulfillment-channel-chart')
        ]),
        dcc.Tab(label='Sales by Size', children=[
            dcc.Graph(id='size-sales-chart')
        ]),
        dcc.Tab(label='Status Distribution', children=[
            dcc.Graph(id='status-distribution-chart')
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
    sales_over_time['Smoothed Amount'] = sales_over_time['Amount'].rolling(window=7).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sales_over_time['Date'], 
        y=sales_over_time['Amount'], 
        mode='lines', 
        name='Original Amount',
        line=dict(color='lightgrey', dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=sales_over_time['Date'], 
        y=sales_over_time['Smoothed Amount'], 
        mode='lines', 
        name='Smoothed Amount',
        line=dict(color='blue')
    ))
    fig.update_layout(
        title='Smooth Sales Trends Over Time',
        xaxis_title='Date',
        yaxis_title='Total Sales',
        template='plotly_white'
    )
    return fig

# Callback to update monthly sales comparison chart
@app.callback(
    Output('monthly-sales-chart', 'figure'),
    Input('monthly-sales-chart', 'id')
)
def update_monthly_sales_chart(_):
    monthly_sales = data.groupby(['Year', 'Month', 'ship-state'])['Amount'].sum().reset_index()
    monthly_sales_pivot = monthly_sales.pivot_table(index=['Year', 'Month'], columns='ship-state', values='Amount', fill_value=0)
    monthly_sales_flat = monthly_sales_pivot.reset_index().melt(id_vars=['Year', 'Month'], var_name='State', value_name='Total Sales')
    
    fig = px.bar(
        monthly_sales_flat, 
        x='Month', 
        y='Total Sales', 
        color='State', 
        barmode='group',
        facet_col='Year',
        title='Monthly Sales Comparison Across States',
        labels={'Month': 'Month', 'Total Sales': 'Total Sales'},
        category_orders={'Month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
    )
    fig.update_layout(
        xaxis=dict(tickmode='array', tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        template='plotly_white'
    )
    return fig

# Callback to update top-selling products chart
@app.callback(
    Output('top-products-chart', 'figure'),
    Input('top-products-chart', 'id')
)
def update_top_products_chart(_):
    top_products = data.groupby('SKU')['Amount'].sum().reset_index().sort_values(by='Amount', ascending=False).head(10)
    
    fig = px.bar(top_products, x='SKU', y='Amount',
                 title='Top-Selling Products',
                 labels={'SKU': 'Product SKU', 'Amount': 'Total Sales'},
                 color='Amount',
                 color_continuous_scale='Blues')
    return fig

# Callback to update top-selling categories chart
@app.callback(
    Output('top-categories-chart', 'figure'),
    Input('top-categories-chart', 'id')
)
def update_top_categories_chart(_):
    top_categories = data.groupby('Category')['Amount'].sum().reset_index().sort_values(by='Amount', ascending=False)
    
    fig = px.bar(top_categories, x='Category', y='Amount',
                 title='Top-Selling Categories',
                 labels={'Category': 'Category', 'Amount': 'Total Sales'},
                 color='Amount',
                 color_continuous_scale='Greens')
    return fig

# Callback to update the impact of promotions on sales
@app.callback(
    Output('promotion-impact-chart', 'figure'),
    Input('promotion-impact-chart', 'id')
)
def update_promotion_impact_chart(_):
    promotion_impact = data.groupby('Promotion Applied')['Amount'].sum().reset_index()
    promotion_impact['Promotion'] = promotion_impact['Promotion Applied'].map({True: 'With Promotion', False: 'Without Promotion'})
    
    fig = px.bar(promotion_impact, x='Promotion', y='Amount',
                 title='Impact of Promotions on Sales',
                 labels={'Promotion': 'Promotion Status', 'Amount': 'Total Sales'},
                 color='Amount',
                 color_continuous_scale='Oranges')
    return fig

# Callback to update sales by fulfillment channel chart
@app.callback(
    Output('fulfillment-channel-chart', 'figure'),
    Input('fulfillment-channel-chart', 'id')
)
def update_fulfillment_channel_chart(_):
    fulfillment_sales = data.groupby('Fulfilment')['Amount'].sum().reset_index()
    
    fig = px.bar(fulfillment_sales, x='Fulfilment', y='Amount',
                 title='Sales by Fulfillment Channel',
                 labels={'Fulfilment': 'Fulfillment Channel', 'Amount': 'Total Sales'},
                 color='Amount',
                 color_continuous_scale='Purples')
    return fig

# Callback to update sales by size chart
@app.callback(
    Output('size-sales-chart', 'figure'),
    Input('size-sales-chart', 'id')
)
def update_size_sales_chart(_):
    sales_by_size = data.groupby('Size')['Amount'].sum().reset_index()
    
    fig = px.bar(sales_by_size, x='Size', y='Amount',
                 title='Sales by Size',
                 labels={'Size': 'Size', 'Amount': 'Total Sales'},
                 color='Amount',
                 color_continuous_scale='Cividis')
    return fig

# Callback to update status distribution chart
@app.callback(
    Output('status-distribution-chart', 'figure'),
    Input('status-distribution-chart', 'id')
)
def update_status_distribution_chart(_):
    status_distribution = data['Status'].value_counts().reset_index()
    status_distribution.columns = ['Status', 'Count']
    
    fig = px.pie(status_distribution, values='Count', names='Status',
                 title='Order Status Distribution',
                 labels={'Count': 'Number of Orders', 'Status': 'Order Status'},
                 color_discrete_sequence=px.colors.sequential.RdBu)
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

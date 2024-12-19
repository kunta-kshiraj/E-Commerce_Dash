import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Load and preprocess the dataset
df = pd.read_csv('OnlineRetail.csv', encoding='latin1')

# Data cleaning
df.dropna(subset=['CustomerID'], inplace=True)
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

# Add additional features
df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
df['Hour'] = df['InvoiceDate'].dt.hour

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
app.title = "Online Retail Dashboard"

# Define the layout with tabs
app.layout = html.Div([
    dbc.NavbarSimple(
        brand="Online Retail Dashboard",
        brand_href="#",
        color="primary",
        dark=True,
    ),
    dbc.Container([
        dbc.Tabs([
            dbc.Tab(label="Overview", tab_id="overview"),
            dbc.Tab(label="Sales Trends", tab_id="sales-trends"),
            dbc.Tab(label="Top Products", tab_id="top-products"),
            dbc.Tab(label="Customer Insights", tab_id="customer-insights"),
        ], id="tabs", active_tab="overview"),
        html.Div(id="tab-content", className="p-4")
    ])
])

# Callback to render content for each tab
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_content(active_tab):
    if active_tab == "overview":
        # KPIs
        total_revenue = df['TotalPrice'].sum()
        unique_customers = df['CustomerID'].nunique()
        total_invoices = df['InvoiceNo'].nunique()

        kpi_cards = dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Total Revenue", className="card-title"),
                    html.H3(f"${total_revenue:,.2f}")
                ])
            ], color="info", inverse=True)),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Unique Customers", className="card-title"),
                    html.H3(f"{unique_customers:,}")
                ])
            ], color="success", inverse=True)),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Total Invoices", className="card-title"),
                    html.H3(f"{total_invoices:,}")
                ])
            ], color="warning", inverse=True))
        ])

        return html.Div([kpi_cards])

    elif active_tab == "sales-trends":
        # Revenue trend over time
        revenue_trend = df.groupby('YearMonth')['TotalPrice'].sum().reset_index()

        # Ensure YearMonth is a string
        revenue_trend['YearMonth'] = revenue_trend['YearMonth'].astype(str)

        # Create the line chart
        fig = px.line(
            revenue_trend, 
            x='YearMonth', 
            y='TotalPrice', 
            title="Revenue Trend Over Time"
        )
        return dcc.Graph(figure=fig)

    elif active_tab == "top-products":
        # Top products by revenue
        top_products = df.groupby('Description')['TotalPrice'].sum().reset_index().nlargest(10, 'TotalPrice')
        fig = px.bar(top_products, x='TotalPrice', y='Description', orientation='h', title="Top Products by Revenue")
        return dcc.Graph(figure=fig)

    elif active_tab == "customer-insights":

        # Revenue by country
        country_revenue = df.groupby('Country')['TotalPrice'].sum().reset_index().nlargest(10, 'TotalPrice')

        # Average Spending per Customer
        avg_spending = df.groupby('CustomerID')['TotalPrice'].mean().reset_index().nlargest(10, 'TotalPrice')

        # Frequency of Purchases per Customer
        purchase_freq = df.groupby('CustomerID')['InvoiceNo'].nunique().reset_index()

        # Revenue by Hour of Day
        revenue_by_hour = df.groupby('Hour')['TotalPrice'].sum().reset_index()

        # Orders Over Time
        orders_over_time = df.groupby('YearMonth')['InvoiceNo'].nunique().reset_index()

        # Ensure YearMonth is a string
        orders_over_time['YearMonth'] = orders_over_time['YearMonth'].astype(str)

        fig_orders_over_time = px.line(
            orders_over_time, 
            x='YearMonth', 
            y='InvoiceNo', 
            title="Number of Orders Over Time"
        )

        # Add visualizations here
        return html.Div([
            dcc.Graph(figure=px.bar(country_revenue, x='TotalPrice', y='Country', orientation='h', title="Revenue by Country")),
            dcc.Graph(figure=px.bar(avg_spending, x='TotalPrice', y='CustomerID', orientation='h', title="Top Customers by Average Spending")),
            dcc.Graph(figure=px.line(revenue_by_hour, x='Hour', y='TotalPrice', title="Revenue by Hour of Day")),
            dcc.Graph(figure=px.line(orders_over_time, x='YearMonth', y='InvoiceNo', title="Number of Orders Over Time")),
            dcc.Graph(figure=px.histogram(purchase_freq, x='InvoiceNo', nbins=20, title="Frequency of Purchases per Customer")),

        ])



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

import streamlit as st
import pandas as pd
import plotly.express as px

# Set the page configuration (must be the first Streamlit command)
st.set_page_config(page_title="Online Retail Dashboard", layout="wide")

# Include Bootstrap CSS
st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .metric-container {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }
        .metric-card {
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .metric-title {
            font-weight: bold;
            font-size: 18px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load and preprocess the dataset
df = pd.read_csv('OnlineRetail.csv', encoding='latin1')

# Data cleaning
df.dropna(subset=['CustomerID'], inplace=True)
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

# Add additional features
df['YearMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)
df['Hour'] = df['InvoiceDate'].dt.hour

# App title and sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Sales Trends", "Top Products", "Customer Insights"])

# Overview Page
if page == "Overview":
    st.title("Overview")

    # KPIs
    total_revenue = df['TotalPrice'].sum()
    unique_customers = df['CustomerID'].nunique()
    total_invoices = df['InvoiceNo'].nunique()

    # Display KPIs with Bootstrap
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-card bg-info text-white">
                <div class="metric-title">Total Revenue</div>
                <div class="metric-value">${total_revenue:,.2f}</div>
            </div>
            <div class="metric-card bg-success text-white">
                <div class="metric-title">Unique Customers</div>
                <div class="metric-value">{unique_customers:,}</div>
            </div>
            <div class="metric-card bg-warning text-dark">
                <div class="metric-title">Total Invoices</div>
                <div class="metric-value">{total_invoices:,}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Sales Trends Page
elif page == "Sales Trends":
    st.title("Sales Trends")

    # Revenue trend over time
    revenue_trend = df.groupby('YearMonth')['TotalPrice'].sum().reset_index()
    fig = px.line(
        revenue_trend,
        x='YearMonth',
        y='TotalPrice',
        title="Revenue Trend Over Time",
        labels={'YearMonth': 'Month', 'TotalPrice': 'Revenue ($)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# Top Products Page
elif page == "Top Products":
    st.title("Top Products")

    # Top products by revenue
    top_products = df.groupby('Description')['TotalPrice'].sum().reset_index().nlargest(10, 'TotalPrice')
    fig = px.bar(
        top_products,
        x='TotalPrice',
        y='Description',
        orientation='h',
        title="Top Products by Revenue",
        labels={'TotalPrice': 'Revenue ($)', 'Description': 'Product'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Customer Insights Page
elif page == "Customer Insights":
    st.title("Customer Insights")

    # Revenue by country
    country_revenue = df.groupby('Country')['TotalPrice'].sum().reset_index().nlargest(10, 'TotalPrice')
    fig_country = px.bar(
        country_revenue,
        x='TotalPrice',
        y='Country',
        orientation='h',
        title="Revenue by Country",
        labels={'TotalPrice': 'Revenue ($)', 'Country': 'Country'}
    )
    st.plotly_chart(fig_country, use_container_width=True)

    # Average Spending per Customer
    avg_spending = df.groupby('CustomerID')['TotalPrice'].mean().reset_index().nlargest(10, 'TotalPrice')
    fig_avg_spending = px.bar(
        avg_spending,
        x='TotalPrice',
        y='CustomerID',
        orientation='h',
        title="Top Customers by Average Spending",
        labels={'TotalPrice': 'Average Spending ($)', 'CustomerID': 'Customer ID'}
    )
    st.plotly_chart(fig_avg_spending, use_container_width=True)

    # Frequency of Purchases per Customer
    purchase_freq = df.groupby('CustomerID')['InvoiceNo'].nunique().reset_index()
    fig_freq = px.histogram(
        purchase_freq,
        x='InvoiceNo',
        nbins=20,
        title="Frequency of Purchases per Customer",
        labels={'InvoiceNo': 'Number of Purchases'}
    )
    st.plotly_chart(fig_freq, use_container_width=True)

    # Revenue by Hour of Day
    revenue_by_hour = df.groupby('Hour')['TotalPrice'].sum().reset_index()
    fig_hour = px.line(
        revenue_by_hour,
        x='Hour',
        y='TotalPrice',
        title="Revenue by Hour of Day",
        labels={'Hour': 'Hour of Day', 'TotalPrice': 'Revenue ($)'}
    )
    st.plotly_chart(fig_hour, use_container_width=True)

    # Orders Over Time
    orders_over_time = df.groupby('YearMonth')['InvoiceNo'].nunique().reset_index()
    fig_orders = px.line(
        orders_over_time,
        x='YearMonth',
        y='InvoiceNo',
        title="Number of Orders Over Time",
        labels={'YearMonth': 'Month', 'InvoiceNo': 'Number of Orders'}
    )
    fig_orders.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_orders, use_container_width=True)

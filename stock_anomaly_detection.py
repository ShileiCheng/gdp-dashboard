import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt

# Set page title and icon
st.set_page_config(
    page_title="Stock Price Visualization",
    page_icon=":chart_with_upwards_trend:"
)

# Page title
st.title(":chart_with_upwards_trend: Stock Price Visualization")

# Directly read the local CSV file
DATA_FILENAME = Path(__file__).parent / 'data' / 'SP600_AdjClose_Volume_Return.csv'
stock_df = pd.read_csv(DATA_FILENAME)

# Convert the Date column to datetime format
stock_df['Date'] = pd.to_datetime(stock_df['Date'], errors='coerce')

# Drop rows where the Date conversion failed (NaT values)
stock_df = stock_df.dropna(subset=['Date'])

# Sort data by date
stock_df = stock_df.sort_values('Date')

# Data preview
st.write("Data Preview:")
st.dataframe(stock_df.head())

# Set up the date range slider
min_date = stock_df['Date'].min().year
max_date = stock_df['Date'].max().year

start_year, end_year = st.slider(
    "Select the range of years you are interested in:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# Filter data based on the selected date range
filtered_df = stock_df[(stock_df['Date'].dt.year >= start_year) & (stock_df['Date'].dt.year <= end_year)]

# Check if filtered data has "Adj Close" and "Ticker" columns for plotting
if 'Adj Close' in filtered_df.columns and 'Ticker' in filtered_df.columns:
    # Use Altair to plot the trend chart based on the filtered data
    line_chart = alt.Chart(filtered_df).mark_line().encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Adj Close:Q', title='Adjusted Close Price'),
        color='Ticker:N'  # Different colors for each stock ticker
    ).properties(
        width=800,
        height=400,
        title=f"Stock Price Trends by Ticker ({start_year} - {end_year})"
    )

    # Display the trend chart
    st.altair_chart(line_chart, use_container_width=True)
else:
    st.error("The file does not contain 'Adj Close' and 'Ticker' columns.")

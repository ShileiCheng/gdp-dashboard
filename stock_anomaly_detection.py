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

# Set up the date range pickers
min_date = stock_df['Date'].min()
max_date = stock_df['Date'].max()

# DATE BOX
start_date = st.date_input("Start Date", min_date)
end_date = st.date_input("End Date", max_date)

# Ensure start_date is before end_date
if start_date > end_date:
    st.error("Error: Start Date must be before End Date.")
else:
    # Dropdown for selecting stock ticker
    ticker_list = stock_df['Ticker'].unique()
    selected_ticker = st.selectbox("Select Stock Ticker", ticker_list)

    # Go button to display the chart
    if st.button("Go"):
        # Filter data based on the selected date range and ticker
        filtered_df = stock_df[(stock_df['Date'] >= pd.to_datetime(start_date)) &
                               (stock_df['Date'] <= pd.to_datetime(end_date)) &
                               (stock_df['Ticker'] == selected_ticker)]

        # Check if filtered data has "Adj Close" column for plotting
        if not filtered_df.empty:
            # Use Altair to plot the trend chart based on the filtered data
            line_chart = alt.Chart(filtered_df).mark_line().encode(
                x=alt.X('Date:T', title='Date'),
                y=alt.Y('Adj Close:Q', title='Adjusted Close Price')
            ).properties(
                width=800,
                height=400,
                title=f"Stock Price Trend for {selected_ticker} ({start_date} - {end_date})"
            )
            # Display the trend chart
            st.altair_chart(line_chart, use_container_width=True)
        else:
            st.error("No data available for the selected date range and ticker.")

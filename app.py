import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt

# Set page title, icon, and default layout (centered)
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon=":chart_with_upwards_trend:"
)


# Load CSS from an external file
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Apply the CSS
load_css("styles.css")

# Page title
st.title(":chart_with_upwards_trend: Stock Analysis Dashboard")

# Load the data files
DATA_FILENAME = Path(__file__).parent / 'data' / 'SP600_AdjClose_Volume_Return.csv'
ANOMALY_FILENAME = Path(__file__).parent / 'data' / 'overall_anomalies.csv'

# Load stock price data
stock_df = pd.read_csv(DATA_FILENAME)
stock_df.columns = stock_df.columns.str.strip()  # Remove any leading/trailing whitespace from column names
stock_df['Date'] = pd.to_datetime(stock_df['Date'], errors='coerce')
stock_df['Adj Close'] = pd.to_numeric(stock_df['Adj Close'], errors='coerce')  # Ensure Adj Close is numeric
stock_df = stock_df.dropna(subset=['Date', 'Adj Close']).sort_values('Date')

# Load anomaly data
anomaly_df = pd.read_csv(ANOMALY_FILENAME)
anomaly_df.columns = anomaly_df.columns.str.strip()  # Remove any leading/trailing whitespace from column names
anomaly_df['Date'] = pd.to_datetime(anomaly_df['Date'], errors='coerce')
anomaly_df = anomaly_df.dropna(subset=['Date']).sort_values('Date')

# Set up the date range and ticker selection
min_date = stock_df['Date'].min()
max_date = stock_df['Date'].max()
start_date = st.date_input("Start Date", min_date)
end_date = st.date_input("End Date", max_date)
ticker_list = stock_df['Ticker'].unique()
selected_ticker = st.selectbox("Select Stock Ticker", ticker_list)

# Model selection dropdown
selected_model = st.selectbox("Select Model", ["Model1"])  # Currently, only "Model1" is available

# Ensure start_date is before end_date
if start_date > end_date:
    st.error("Error: Start Date must be before End Date.")
else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Stock Price", "Anomaly Detection", "Model Explanation"])

    # Tab 1: Stock Price Visualization
    with tab1:
        st.header("Stock Price Visualization")

        # Filter stock data based on the selected date range and ticker
        filtered_stock_df = stock_df[(stock_df['Date'] >= pd.to_datetime(start_date)) &
                                     (stock_df['Date'] <= pd.to_datetime(end_date)) &
                                     (stock_df['Ticker'] == selected_ticker)]

        if not filtered_stock_df.empty:
            # Plot stock price trend
            line_chart = alt.Chart(filtered_stock_df).mark_line().encode(
                x=alt.X('Date:T', title='Date'),
                y=alt.Y('Adj Close:Q', title='Adjusted Close Price')
            ).properties(
                width=700,
                height=400,
                title=f"Stock Price Trend for {selected_ticker} ({start_date} - {end_date}) using {selected_model}"
            )
            st.altair_chart(line_chart, use_container_width=True)
        else:
            st.error("No data available for the selected date range and ticker.")

    # Tab 2: Anomaly Detection
    with tab2:
        st.header("Anomaly Detection")

        # Filter stock data based on the selected date range and ticker
        filtered_stock_df = stock_df[(stock_df['Date'] >= pd.to_datetime(start_date)) &
                                     (stock_df['Date'] <= pd.to_datetime(end_date)) &
                                     (stock_df['Ticker'] == selected_ticker)]

        # Filter anomaly data based on the selected date range and ticker
        filtered_anomaly_df = anomaly_df[(anomaly_df['Date'] >= pd.to_datetime(start_date)) &
                                         (anomaly_df['Date'] <= pd.to_datetime(end_date)) &
                                         (anomaly_df['Ticker'] == selected_ticker) &
                                         (anomaly_df['Overall_Anomaly'] == 1)]  # Only anomalies

        # Merge anomaly data with stock price data to get the 'Adj Close' for anomaly points
        merged_anomaly_df = pd.merge(filtered_anomaly_df, filtered_stock_df[['Date', 'Ticker', 'Adj Close']],
                                     on=['Date', 'Ticker'], how='inner')

        if not filtered_stock_df.empty:
            # Plot stock price trend
            line_chart = alt.Chart(filtered_stock_df).mark_line().encode(
                x=alt.X('Date:T', title='Date'),
                y=alt.Y('Adj Close:Q', title='Adjusted Close Price')
            )

            # Mark anomaly points if any
            if not merged_anomaly_df.empty:
                anomaly_points = alt.Chart(merged_anomaly_df).mark_circle(size=60, color='red').encode(
                    x='Date:T',
                    y='Adj Close:Q',
                    tooltip=['Date', 'Adj Close']
                )
                # Combine line chart and anomaly points
                combined_chart = (line_chart + anomaly_points).properties(
                    width=700,
                    height=400,
                    title=f"Stock Price with Anomalies for {selected_ticker} ({start_date} - {end_date}) using {selected_model}"
                )
            else:
                # If no anomalies, show only the line chart
                combined_chart = line_chart.properties(
                    width=700,
                    height=400,
                    title=f"Stock Price Trend for {selected_ticker} ({start_date} - {end_date}) using {selected_model}"
                )

            st.altair_chart(combined_chart, use_container_width=True)
        else:
            st.error("No data available for the selected date range and ticker.")

    # Tab 3: Model Explanation
    with tab3:
        st.header("Model Explanation")
        st.write("In this section, you can explain the model used for analysis.")

        st.subheader("Model Overview")
        st.write(f"""
        {selected_model} uses a combination of supervised and unsupervised learning techniques to detect stock price anomalies. 
        Various features such as moving averages, volatility, and volume are included to enhance detection accuracy.
        """)
        st.subheader("Key Features Used")
        st.write("""
        - Rolling mean and standard deviation of returns
        - Price momentum calculated from adjusted close prices
        - Sentiment analysis from associated news data (if available)
        """)
        st.subheader("Future Improvements")
        st.write("""
        Future enhancements could include more robust feature engineering, additional anomaly detection algorithms, 
        and integrating real-time data for live anomaly detection.
        """)

import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt

# Set page title, icon, and default layout
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon=":chart_with_upwards_trend:"
)

# Load CSS from an external file
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CSS file not found. Please ensure 'styles.css' is in the correct location.")

# Apply the CSS
load_css("styles.css")

# Page title
st.title(":chart_with_upwards_trend: Stock Analysis Dashboard")

# Load data files
DATA_FILENAME = Path(__file__).parent / 'data' / 'SP600_AdjClose_Volume_Return.csv'
FULL_DATA_FILENAME = Path(__file__).parent / 'data' / 'full_table.csv'

# Load stock price data
stock_df = pd.read_csv(DATA_FILENAME)
stock_df.columns = stock_df.columns.str.strip()
stock_df['Date'] = pd.to_datetime(stock_df['Date'], errors='coerce')
stock_df['Adj Close'] = pd.to_numeric(stock_df['Adj Close'], errors='coerce')
stock_df = stock_df.dropna(subset=['Date', 'Adj Close']).sort_values('Date')

# Load anomaly data from full_data.csv
full_data_df = pd.read_csv(FULL_DATA_FILENAME)
full_data_df.columns = full_data_df.columns.str.strip()
full_data_df['Date'] = pd.to_datetime(full_data_df['Date'], errors='coerce')
full_data_df = full_data_df.dropna(subset=['Date']).sort_values('Date')

# Set up the date range and ticker selection
min_date = stock_df['Date'].min()
max_date = stock_df['Date'].max()
start_date = st.date_input("Start Date", min_date)
end_date = st.date_input("End Date", max_date)
ticker_list = stock_df['Ticker'].unique()
selected_ticker = st.selectbox("Select Stock Ticker", ticker_list)

# Model selection dropdowns for anomaly comparison
model_options = ["baseline", "svm", "dbscan_pca", "dbscan_nonpca", "isolation tree"]
model_1 = st.selectbox("Select First Model", model_options)
model_2 = st.selectbox("Select Second Model", model_options)

# Ensure start_date is before end_date
if start_date > end_date:
    st.error("Error: Start Date must be before End Date.")
else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Stock Prices", "Anomaly Comparison", "Model Explanation"])

    # Tab 1: Stock Prices
    with tab1:
        st.header("Stock Price Visualization")

        # Filter stock data based on date range and ticker
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
                title=f"Stock Price Trend for {selected_ticker} ({start_date} - {end_date})"
            )
            st.altair_chart(line_chart, use_container_width=True)
        else:
            st.error("No data available for the selected date range and ticker.")

    # Tab 2: Anomaly Comparison
    with tab2:
        st.header("Anomaly Comparison")

        # Filter stock data based on date range and ticker
        filtered_stock_df = stock_df[(stock_df['Date'] >= pd.to_datetime(start_date)) &
                                     (stock_df['Date'] <= pd.to_datetime(end_date)) &
                                     (stock_df['Ticker'] == selected_ticker)]

        # Filter anomaly data for both models
        model_1_anomalies = full_data_df[(full_data_df['Date'] >= pd.to_datetime(start_date)) &
                                         (full_data_df['Date'] <= pd.to_datetime(end_date)) &
                                         (full_data_df['Ticker'] == selected_ticker) &
                                         (full_data_df[model_1] == 1)]

        model_2_anomalies = full_data_df[(full_data_df['Date'] >= pd.to_datetime(start_date)) &
                                         (full_data_df['Date'] <= pd.to_datetime(end_date)) &
                                         (full_data_df['Ticker'] == selected_ticker) &
                                         (full_data_df[model_2] == 1)]

        # Find overlapping anomalies
        overlapping_anomalies = pd.merge(model_1_anomalies, model_2_anomalies, on=['Date', 'Ticker'])

        # Merge anomalies with stock price data
        model_1_merged = pd.merge(model_1_anomalies, filtered_stock_df[['Date', 'Ticker', 'Adj Close']],
                                  on=['Date', 'Ticker'], how='inner')

        model_2_merged = pd.merge(model_2_anomalies, filtered_stock_df[['Date', 'Ticker', 'Adj Close']],
                                  on=['Date', 'Ticker'], how='inner')

        overlapping_merged = pd.merge(overlapping_anomalies, filtered_stock_df[['Date', 'Ticker', 'Adj Close']],
                                      on=['Date', 'Ticker'], how='inner')

        # Visualize
        if not filtered_stock_df.empty:
            # Base line chart for stock prices
            line_chart = alt.Chart(filtered_stock_df).mark_line().encode(
                x=alt.X('Date:T', title='Date'),
                y=alt.Y('Adj Close:Q', title='Adjusted Close Price')
            )

            # Anomalies for Model 1
            model_1_points = alt.Chart(model_1_merged).mark_circle(size=60, color='blue').encode(
                x='Date:T',
                y='Adj Close:Q',
                tooltip=['Date', 'Adj Close']
            )

            # Anomalies for Model 2
            model_2_points = alt.Chart(model_2_merged).mark_circle(size=60, color='red').encode(
                x='Date:T',
                y='Adj Close:Q',
                tooltip=['Date', 'Adj Close']
            )

            # Overlapping anomalies
            overlap_points = alt.Chart(overlapping_merged).mark_circle(size=80, color='purple').encode(
                x='Date:T',
                y='Adj Close:Q',
                tooltip=['Date', 'Adj Close']
            )

            # Combine charts
            combined_chart = (line_chart + model_1_points + model_2_points + overlap_points).properties(
                width=700,
                height=400,
                title=f"Anomaly Comparison: {model_1.capitalize()} (Blue), {model_2.capitalize()} (Red), Overlap (Purple)"
            )

            # Display chart
            st.altair_chart(combined_chart, use_container_width=True)

            # Legend
            st.write("### Legend")
            st.markdown("""
            - **Blue**: Anomalies detected by the first model.
            - **Red**: Anomalies detected by the second model.
            - **Purple**: Overlapping anomalies detected by both models.
            """)
        else:
            st.error("No data available for the selected date range and ticker.")

    # Tab 3: Model Explanation
    with tab3:
        st.header("Model Explanation")
        st.subheader(f"Explanation for {model_1.capitalize()}")
        st.write(f"{model_1.capitalize()} model details go here...")

        st.subheader(f"Explanation for {model_2.capitalize()}")
        st.write(f"{model_2.capitalize()} model details go here...")

import pandas as pd
from pathlib import Path

# Define file paths
ANOMALY_FILENAME = Path(__file__).parent / 'data' / 'overall_anomalies.csv'
SVM_ANOMALIES_FILENAME = Path(__file__).parent / 'data' / 'svm_anomalies.csv'
DBSCAN_ANOMALIES_FILENAME = Path(__file__).parent / 'data' / 'anomalies_dbscan_pca.csv'

# Load data
overall_anomalies = pd.read_csv(ANOMALY_FILENAME)
svm_anomalies = pd.read_csv(SVM_ANOMALIES_FILENAME)
dbscan_anomalies = pd.read_csv(DBSCAN_ANOMALIES_FILENAME)

# Add 'svm_match' column by checking if each 'Ticker' and 'Date' in overall_anomalies exists in svm_anomalies
overall_anomalies['svm_match'] = overall_anomalies.merge(
    svm_anomalies[['Ticker', 'Date']], on=['Ticker', 'Date'], how='left', indicator=True
)['_merge'].eq('both').astype(int)

# Add 'dbscan_match' column by checking if each 'Ticker' and 'Date' in overall_anomalies exists in dbscan_anomalies
overall_anomalies['dbscan_match'] = overall_anomalies.merge(
    dbscan_anomalies[['Ticker', 'Date']], on=['Ticker', 'Date'], how='left', indicator=True
)['_merge'].eq('both').astype(int)

# Display result
print(overall_anomalies.head(50))

# Define the output file path
output_file = Path(__file__).parent / 'data' / 'full_table.csv'

# Save the DataFrame to a CSV file
overall_anomalies.to_csv(output_file, index=False)
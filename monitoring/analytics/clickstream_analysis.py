import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import logging

# Configure logging
logging.basicConfig(filename='clickstream_analysis.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# Constants
DATA_DIR = './clickstream_data'
CLUSTER_COUNT = 5

# Load clickstream data
def load_clickstream_data(file_path):
    try:
        logging.info(f'Loading clickstream data from {file_path}')
        with open(file_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except Exception as e:
        logging.error(f'Error loading clickstream data: {e}')
        return pd.DataFrame()

# Preprocess clickstream data
def preprocess_data(df):
    logging.info('Preprocessing data')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['click_duration'] = df.groupby('session_id')['timestamp'].diff().dt.total_seconds().fillna(0)
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df.fillna(0, inplace=True)
    return df

# Analyze sessions
def session_analysis(df):
    logging.info('Analyzing sessions')
    session_durations = df.groupby('session_id')['click_duration'].sum()
    session_clicks = df.groupby('session_id').size()
    return pd.DataFrame({'session_duration': session_durations, 'session_clicks': session_clicks})

# Cluster users based on behavior
def user_clustering(df, n_clusters=CLUSTER_COUNT):
    logging.info('Clustering users based on click behavior')
    scaler = StandardScaler()
    X = df[['session_duration', 'session_clicks']]
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    return df

# Plot cluster distribution
def plot_clusters(df):
    logging.info('Plotting cluster distribution')
    plt.figure(figsize=(8, 6))
    plt.hist(df['cluster'], bins=CLUSTER_COUNT, edgecolor='black')
    plt.title('User Behavior Clusters')
    plt.xlabel('Cluster')
    plt.ylabel('Frequency')
    plt.savefig('cluster_distribution.png')
    plt.show()

# Analyze click paths
def click_path_analysis(df):
    logging.info('Analyzing click paths')
    df['click_path'] = df.groupby('session_id')['page_id'].transform(lambda x: ' -> '.join(x.astype(str)))
    click_paths = df.groupby('click_path').size().sort_values(ascending=False).reset_index()
    click_paths.columns = ['click_path', 'count']
    return click_paths

# Analyze click frequency by hour
def hourly_click_analysis(df):
    logging.info('Analyzing hourly click frequency')
    hourly_clicks = df.groupby('hour').size()
    plt.figure(figsize=(10, 6))
    plt.plot(hourly_clicks.index, hourly_clicks.values, marker='o')
    plt.title('Hourly Click Frequency')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Clicks')
    plt.grid(True)
    plt.savefig('hourly_click_frequency.png')
    plt.show()

# Analyze click frequency by day of week
def daily_click_analysis(df):
    logging.info('Analyzing daily click frequency')
    daily_clicks = df.groupby('day_of_week').size()
    plt.figure(figsize=(10, 6))
    plt.bar(daily_clicks.index, daily_clicks.values)
    plt.title('Click Frequency by Day of the Week')
    plt.xlabel('Day of the Week (0=Monday)')
    plt.ylabel('Number of Clicks')
    plt.grid(True)
    plt.savefig('daily_click_frequency.png')
    plt.show()

# Save results to CSV
def save_results(df, session_summary, click_paths):
    logging.info('Saving analysis results to CSV')
    try:
        df.to_csv(os.path.join(DATA_DIR, 'preprocessed_clickstream.csv'), index=False)
        session_summary.to_csv(os.path.join(DATA_DIR, 'session_summary.csv'), index=False)
        click_paths.to_csv(os.path.join(DATA_DIR, 'click_paths.csv'), index=False)
    except Exception as e:
        logging.error(f'Error saving results: {e}')

# Main analysis pipeline
def clickstream_analysis_pipeline(file_path):
    logging.info('Starting clickstream analysis pipeline')
    
    # Load and preprocess data
    df = load_clickstream_data(file_path)
    if df.empty:
        logging.error('No data to process, exiting pipeline')
        return

    df = preprocess_data(df)

    # Perform session analysis
    session_summary = session_analysis(df)
    
    # Perform clustering analysis
    df = user_clustering(session_summary)

    # Analyze click paths
    click_paths = click_path_analysis(df)

    # Analyze click frequency patterns
    hourly_click_analysis(df)
    daily_click_analysis(df)

    # Plot clusters
    plot_clusters(df)

    # Save the results
    save_results(df, session_summary, click_paths)

    logging.info('Clickstream analysis pipeline completed')

# Execute the clickstream analysis pipeline
if __name__ == '__main__':
    clickstream_file = os.path.join(DATA_DIR, 'clickstream_data.json')
    clickstream_analysis_pipeline(clickstream_file)
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time

# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) for API endpoints

# Global variables for data streaming and anomaly detection
data_stream = []          # Holds the real-time data stream
anomaly_flags = []        # Holds the anomaly flags (1 for anomaly, 0 for normal)
current_index = 0         # Tracks the index of the current data point being streamed
lock = threading.Lock()   # Lock for thread-safe access to shared resources

# Parameters for anomaly detection
selected_dataset = 'SKAB/data/valve1/1.csv'  # Path to dataset file
z_threshold = 2.3                            # Z-score threshold for anomalies

# Processing time tracking
total_processing_time = 0.0  # Total processing time of anomaly detection
processed_points = 0         # Count of total data points processed

# Function to load the dataset
def load_dataset():
    """
    Load and preprocess the dataset from the specified path.
    The 'Current' column is used for anomaly detection.
    """
    try:
        # Load the dataset, parse the 'datetime' column
        df = pd.read_csv(selected_dataset, sep=';', parse_dates=['datetime'])
        # Ensure 'Current' is of type float
        df['Current'] = df['Current'].astype(float)
        # Format 'datetime' to a string format
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        # Return only the relevant columns as a list of dictionaries
        return df[['datetime', 'Current']].to_dict(orient='records')
    except FileNotFoundError:
        print(f"Error: The file {selected_dataset} was not found.")
        exit(1)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        exit(1)

# Holds the entire dataset after loading
data = []

# Function to calculate the Z-score for anomaly detection
def calculate_z_score(value, mean, std):
    """
    Calculate the Z-score of a value relative to the dataset's mean and standard deviation.
    Parameters:
        value (float): The data point value.
        mean (float): The mean of the data.
        std (float): The standard deviation of the data.
    Returns:
        float: The Z-score of the value.
    """
    if std == 0:  # Avoid division by zero
        return 0
    return (value - mean) / std

# Function to simulate streaming data and detect anomalies
def stream_data():
    """
    Simulates a real-time data stream by processing one data point at a time
    and detecting anomalies using the Z-score method.
    """
    global data_stream, anomaly_flags, current_index, data
    global total_processing_time, processed_points

    while True:
        if not data:
            # Load data if not already loaded
            data = load_dataset()

        # Simulate streaming one data point at a time
        while current_index < len(data):
            time.sleep(0.1)  # Delay to simulate real-time data streaming
            data_point = data[current_index]  # Get the current data point

            with lock:  # Ensure thread-safe access to shared resources
                start_time = time.time()  # Record start time for processing

                # Append the current data point to the stream
                data_stream.append(data_point)

                # Perform anomaly detection after at least 50 data points are collected
                if len(data_stream) > 50:
                    # Use the last 50 points for calculating mean and standard deviation
                    current_values = [d['Current'] for d in data_stream[-50:]]
                    mean = sum(current_values) / len(current_values)
                    std = pd.Series(current_values).std()

                    # Calculate Z-score for the current data point
                    z_score = calculate_z_score(data_point['Current'], mean, std)

                    # Flag as anomaly if the absolute Z-score exceeds the threshold
                    is_anomaly = abs(z_score) > z_threshold
                    anomaly_flags.append(1 if is_anomaly else 0)
                else:
                    # Not enough data yet to perform anomaly detection
                    anomaly_flags.append(0)

                end_time = time.time()  # Record end time for processing
                # Calculate processing time in milliseconds
                processing_time = (end_time - start_time) * 1000
                total_processing_time += processing_time  # Update total processing time
                processed_points += 1  # Increment processed data points count

                current_index += 1  # Move to the next data point

        # Reset the stream and start from the beginning when all data is processed
        with lock:
            current_index = 0
            data_stream = []
            anomaly_flags = []
            total_processing_time = 0.0
            processed_points = 0

# API endpoint to get the latest data and anomaly flags
@app.route('/api/data', methods=['GET'])
def get_data():
    """
    API endpoint to get the most recent 100 data points and their corresponding anomaly flags.
    Returns:
        JSON response containing data points and anomaly flags.
    """
    with lock:  # Thread-safe access to data
        response_data = {
            'data_points': data_stream[-100:],     # Last 100 data points
            'anomaly_flags': anomaly_flags[-100:]  # Corresponding anomaly flags
        }
    return jsonify(response_data)

# API endpoint to get real-time metrics
@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    API endpoint to get metrics on the data processing, including:
    - Total points processed
    - Anomalies detected
    - Average processing time per point
    - Average 'Current' value
    Returns:
        JSON response containing the metrics.
    """
    with lock:  # Thread-safe access to metrics
        total_points = len(data_stream)
        anomalies_detected = sum(anomaly_flags)
        average_processing_time = (total_processing_time / processed_points) if processed_points > 0 else 0.0
        average_current_value = (sum(float(d['Current']) for d in data_stream) / total_points) if total_points > 0 else 0.0

    metrics = {
        'total_points': total_points,
        'anomalies_detected': anomalies_detected,
        'average_processing_time': average_processing_time,  # In milliseconds
        'average_current_value': average_current_value
    }
    return jsonify(metrics)

# Main function to start the streaming thread and Flask app
if __name__ == '__main__':
    # Start the data streaming in a separate thread
    data_thread = threading.Thread(target=stream_data)
    data_thread.start()

    # Run the Flask application
    app.run(debug=True)

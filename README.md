# Real-Time Anomaly Detection Dashboard

![dashboard](https://github.com/user-attachments/assets/3f295289-8bab-4c67-87d9-b7fb297c369b)

This project implements a **Real-Time Anomaly Detection Dashboard** that monitors streaming data and detects anomalies using the **Z-score method**. It consists of a Python backend using Flask and a React frontend with TypeScript. The application simulates real-time data streaming from a dataset, performs anomaly detection, and visualizes the results on an interactive dashboard.

## Explanation of the Chosen Algorithm: Z-score Anomaly Detection

The **Z-score** is a statistical measure that describes a value's relationship to the mean of a group of values, measured in terms of standard deviations. It is calculated using the formula:

 z = (x-μ)/σ

- **x**: The data point value.
- **μ**: The mean of the dataset.
- **σ**: The standard deviation of the dataset.

### Effectiveness of the Z-score Method

1. **Simplicity**: The Z-score method is straightforward to implement, requiring basic statistical calculations without complex algorithms.

2. **Efficiency**: It requires minimal computational resources, making it suitable for real-time applications where quick processing is essential.

3. **Real-Time Capability**: Since it only needs the mean and standard deviation of recent data points, it can efficiently process streaming data.

4. **Assumption of Normality**: It assumes that the data follows a normal distribution, which is a reasonable approximation for many real-world datasets.

5. **Thresholding**: By setting a predefined threshold (e.g., 2.3 standard deviations), the method effectively flags data points that significantly deviate from the norm as anomalies.

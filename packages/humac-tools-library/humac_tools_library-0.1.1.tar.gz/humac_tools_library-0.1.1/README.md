humac_tools Library
humac_tools is a simple Python library that provides a collection of functions for data analysis, feature engineering, G-code optimization, and utility operations. It includes tools for correlation analysis, seasonality detection, anomaly detection, Pareto analysis, JWT decoding, color classification, and more. This library is designed to simplify common data science and manufacturing analytics tasks.

Installation
You can install the library using pip. Run the following command in your terminal:

text
pip install humac_tools_library
Features
Correlation Analysis: Identify highly correlated and dependent features using Pearson correlation and mutual information.

Seasonality Detection: Analyze time series data for trends, seasonality, and recurring patterns (daily/hourly).

Anomaly Detection: Detect and summarize outliers in time series data.

Pareto Analysis: Identify major contributors to time loss or downtime in manufacturing data.

G-code Optimization: Optimize CNC toolpaths using nearest neighbor algorithms to reduce travel distance.

JWT Decoding: Decode JWT tokens to extract user claims.

Color Classification: Classify feature values into Green, Amber, or Red based on thresholds.

Utility Functions: Includes addition, subtraction, and greeting functions.

Usage
After installation, you can use the library in your Python scripts as follows:

python
from humac_tools import correlation, analyzeSeasonality, anomaliesDetect, paretoAnalysis, optimizedGcode

# Example: Correlation analysis
result = correlation(json_data, target_col="oee")
print(result)

# Example: Seasonality analysis
seasonality = analyzeSeasonality(json_data, target="cycletime", freq='D')
print(seasonality)

# Example: Anomaly detection
anomalies = anomaliesDetect(json_data, target_col="downtime")
print(anomalies)

# Example: Pareto analysis
pareto = paretoAnalysis(json_data, category_column="machineid", feature_name="breakdown_time")
print(pareto)

# Example: G-code optimization
optimized = optimizedGcode(raw_gcode)
print(optimized["updated_gcode"])

Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request. Contributions are welcome!

License
This project is licensed under the MIT License – see the LICENSE file for details.
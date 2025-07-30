import json
import re
import pandas as pd
import numpy as np


### Correlation Function ###
from sklearn.feature_selection import mutual_info_regression
from datetime import datetime as dt
from typing import Dict, Any

def filterIQRoutliers_ex_target0(json_data, target_col):
    """
    Eliminates the outliers from all the numeirc features of the data after imputing the null values with the mean 
    of respective columns. The mean is calculated by temporarily dropping the null values and removing the outliers.
    This function is used in the dependency agent which evaluates the correlation, MI, and MIC of the features.
    
    Parameters:
    - json_data: A list of dictionaries containing the data.
    - target_col: The name of the feature (column) whose outliers need to be filtered along with the other covariate features.
    
    Returns:
    - A clean dataframe after removing the outliers and imputing the null values with the feature mean.
    """
    # Step 1: Convert JSON to DataFrame
    df = pd.DataFrame(json_data)
    # Step 2: Remove rows where target == 0 if they are more than 30%
    zero_target_ratio = (df[target_col] == 0).mean()
    if zero_target_ratio > 0.3:
        df = df[df[target_col] != 0]
    try:
        # Step 3: Identify columns for IQR outlier removal
        default_cols = ['date','timestamp','hour_of_the_day_x','day_of_the_week','week_of_the_month_x','month_of_the_year','tenantid',
                        'v2tenant','week_of_the_month_y', 'start_timestamp', 'datetime','hour', 'end_timestamp','hour_of_the_day_y']
        null_only_cols = df.columns[df.isnull().all()].tolist()
        outlier_cols = [
            col for col in df.columns
            if col not in default_cols and col not in null_only_cols and col != target_col and df[col].dtype in [np.float64, np.int64]
        ]      
        for col in outlier_cols + [target_col]:
            # Step 1: Temporarily drop rows where this column is null
            temp_col_data = df[[col]].dropna()
            # Step 2: Compute IQR bounds for this column
            Q1 = temp_col_data[col].quantile(0.25)
            Q3 = temp_col_data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            # Step 3: Filter out outliers
            cleaned_col_data = temp_col_data[(temp_col_data[col] >= lower) & (temp_col_data[col] <= upper)]
            # Step 4: Compute mean of cleaned data
            clean_mean = cleaned_col_data[col].mean()
            # Step 5: Impute original column's nulls with cleaned mean
            df[col] = df[col].fillna(clean_mean)
        # Step 7: Final outlier removal on fully imputed df
        for col in outlier_cols + [target_col]:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower) & (df[col] <= upper)]
    except Exception as e:
        print("Returning data as it as by skipping outlier treatment due to ", e)
    return df
def correlation(json_data, target_col):  
    """
    Finds the highly correlated and highly dependent features with the target feature using techniques like pearson correlation, 
    mutual information, and maximal information coefficient. The features which are common in top 5 highly dependent features using MI,
    top 5 highly dependent features using MIC, and highly correlated features having pearson correlation greater than abs(0.5) are 
    considered as the highly correlated and dependent features to the target feature. 
    
    Parameters:
    - json_data: A list of dictionaries containing the data.
    - target_col: The name of the feature (column) whose dependency analysis is executed with the other covariate features.
    
    Returns:
    - A json with the target column mentioned and the highly correlated and dependent features to the target.

    Prompt examples:
    - What are the highly dependent features to oee?
    - Find the correlation of cycletime with ooe
    - How is load_percent correlated to cycletime
    """
    final_result = []
    df = pd.DataFrame(json_data)
    for machine in df['machineid'].unique():
        machine_result = {}
        try:
            machine_data_df = df[df['machineid']==machine]
            machine_data = machine_data_df.to_dict(orient='records')
            cleaned_df = filterIQRoutliers_ex_target0(machine_data, target_col)
            default_cols = ['date','timestamp','hour_of_the_day_x','day_of_the_week','week_of_the_month_x','month_of_the_year','tenantid',
                        'v2tenant','week_of_the_month_y', 'start_timestamp', 'datetime','hour', 'end_timestamp','hour_of_the_day_y']
            null_only_cols = cleaned_df.columns[cleaned_df.isnull().all()].tolist()
            numeric_cols = [
                col for col in cleaned_df.columns
                if col not in default_cols and col not in null_only_cols and cleaned_df[col].dtype in [np.float64, np.int64]
            ]
            numeric_df = cleaned_df[numeric_cols]
            if target_col not in numeric_df.columns:
                return {
                    'machine id': machine,
                    'message': 'The target column is not available in the data set'
                }
            # Step 3: Separate features and target
            X = numeric_df.drop(columns=[target_col])
            y = numeric_df[target_col]
            if not X.empty:
                if len(numeric_df) >= 5:
                    # Step 4: Pearson correlation
                    corr_values = numeric_df.corr().loc[target_col].drop(labels=[target_col])
                    strong_corr = corr_values[(corr_values > 0.5) | (corr_values < -0.5)]
                    strong_corr = strong_corr.dropna().to_dict()
                    # Step 5: Mutual Information
                    mi_scores = mutual_info_regression(X, y, discrete_features='auto')
                    mi_dict = dict(zip(X.columns, mi_scores))
                    top_mi = dict(sorted(mi_dict.items(), key=lambda x: x[1], reverse=True)[:5])
                    
                    # Step 7: Identify common features
                    common_features = list(set(strong_corr.keys()) & set(top_mi.keys()))
                    machine_result = {
                    "machine id": machine,
                    "target": target_col,
                    "result": (
                        f"Highly correlated features with target {target_col} based on Pearson and MI: {', '.join(common_features)}"
                        if common_features
                        else f"There are no common features between Pearson correlation and Mutual Information that are highly correlated with the target '{target_col}'."
                    )
                    }
                else:
                    machine_result = {
                    'machine id': machine,
                    'message': f"Insufficient data (only {len(numeric_df)} samples) to compute mutual information. Minimum 5 required."
                }
            else:
                machine_result = {
                    'machine id': machine,
                    'message': 'There are no covariate columns along with the target column to do correlation analysis on.'
                }
        except Exception as e:
            machine_result = {
                'machine id': machine,
                'error': e
            }
        final_result.append(machine_result)
    return final_result

#### Seasonality Analysis Function ####
from datetime import datetime as dt
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import acf
from scipy.signal import find_peaks
from scipy.stats import linregress
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.stattools import acf, pacf

def analyzeSeasonality(json_data, target, freq):
    """
    Analyzes time series data to detect trend, seasonality, and recurring patterns.
    - Aggregates data to daily or hourly frequency.
    - Uses ACF and STL decomposition to identify dominant seasonality and trend direction.
    - Describes recurring hourly/daily patterns and classifies seasonality as additive or multiplicative.
    
    Parameters:
    - json_data: A list of dictionaries containing the data.
    - target_col: The name of the feature (column) whose trend and seasonality patterns needs to be analysed.
    
    Returns:
    - A dictionary with natural language descriptions of trend, seasonality, and pattern.

    Prompt examples:
    - Summarize the daily trend and seasonality in cycletime.
    - Is there a weekly seasonal pattern in the oee attribute?
    - Where are the peaks and troughs for last month's downtime data.
    """
    print("Analyzing seasonality...")
    
    df = pd.DataFrame(json_data)
    #df['timestamp'] = pd.to_datetime(df['date']) + pd.to_timedelta(df['hour_of_the_day'], unit='h')
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df['date'] = df['timestamp'].dt.date
    df.set_index('timestamp', inplace=True)
    df[target] = df[target].fillna(0)
    # Step 2: Frequency-based aggregation
    if freq == 'D':
         # Select only numeric columns for aggregation
        numeric_cols = df.select_dtypes(include=['number'])
        df = numeric_cols.resample('D').mean()
    elif freq == 'H':
        pass  
    else:
        raise ValueError("Invalid frequency. Use 'H' for hourly or 'D' for daily.")
    filled_values = df[target].values
    timestamps = df.index.to_list()
    # Step 3: ACF to find dominant seasonality period
    acf_vals = acf(filled_values, nlags=min(50, len(filled_values)//2), fft=True)
    peaks, _ = find_peaks(acf_vals)
    dominant_period = peaks[1] if len(peaks) > 1 else (24 if freq == 'H' else 7)
    # STL decomposition
    stl = STL(filled_values, period=dominant_period)
    result = stl.fit()
    trend = result.trend
    seasonal = result.seasonal
    resid = result.resid
    # Step 4: Trend analysis
    x = np.arange(len(trend))
    slope, _, _, _, _ = linregress(x, trend)
    trend_dir = "increasing" if slope > 0 else "decreasing" if slope < 0 else "flat"
    trend_desc = f"The trend is {trend_dir} over time with a slope of {slope:.4f}."
    # Step 5: Seasonality analysis
    seasonal_peak_idx = np.argmax(seasonal)
    seasonal_trough_idx = np.argmin(seasonal)
    peak_time = timestamps[seasonal_peak_idx] if seasonal_peak_idx < len(timestamps) else 'Unknown'
    trough_time = timestamps[seasonal_trough_idx] if seasonal_trough_idx < len(timestamps) else 'Unknown'
    # Compare standard deviation of seasonal component relative to trend
    seasonal_strength = np.std(seasonal) / (np.mean(np.abs(trend)) + 1e-6)
    # If the strength of seasonal component changes significantly with trend level, assume multiplicative
    seasonality_type = "multiplicative" if seasonal_strength > 0.5 else "additive"
    # seasonality_type = "additive" if min(filled_values) > 0 else "multiplicative"
    seasonality_desc = (
        f"The seasonality is {seasonality_type} with a dominant period of {dominant_period} "
        f"{'hours' if freq == 'H' else 'days'}. "
        f"Peaks occur around {peak_time}, and troughs occur around {trough_time}."
    )
    # Step 6: Pattern description (hourly or daily)
    if freq == 'H':
        df['hour'] = df.index.hour
        hourly_avg = df.groupby('hour')[target].mean()
        peak_hour = int(hourly_avg.idxmax())
        trough_hour = int(hourly_avg.idxmin())
        pattern_desc = f"Hourly pattern shows peaks around {peak_hour}:00 and lows around {trough_hour}:00."
    else:
        df['dayofweek'] = df.index.dayofweek
        daily_avg = df.groupby('dayofweek')[target].mean()
        day_map = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        peak_day = day_map[int(daily_avg.idxmax())]
        trough_day = day_map[int(daily_avg.idxmin())]
        pattern_desc = f"Daily pattern shows peaks on {peak_day} and lows on {trough_day}."
    # Step 7: Compile and return results
    return {
        "trend": trend_desc,
        "seasonality": seasonality_desc,
        "pattern": pattern_desc
    }

# Function to get downtime categorization pareto
def getDowntimeCategorizationPareto(json_data):
    """
    The getDowntimeCategorizationPareto function processes downtime data provided in JSON format to identify significant categories contributing to total breakdown time.

    Input:
    json_data: A non-empty list of dictionaries containing at least two keys:
    downtime_subtype: The specific type of downtime.
    breakdown_time: The duration of each downtime incident.
    
    Output:
    A dictionary where keys are integers representing the rank of the subtype, and values are another dictionary containing the subtype name and its percentage contribution. If no significant contributors are found, a message indicating this is returned.
    """

    try:
        if not isinstance(json_data, list) or not json_data:
            raise ValueError("The input json_data must be a non-empty list or a valid JSON string.")

        df = pd.DataFrame(json_data)

        if df.empty:
            raise ValueError("The DataFrame created from the JSON data is empty.")

        required_columns = ['downtime_subtype', 'breakdown_time']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        breakdown_time = df.groupby('downtime_subtype')['breakdown_time'].sum()
        total_downtime = breakdown_time.sum()
        if total_downtime == 0:
            raise ValueError("The total breakdown time is zero, unable to calculate percentages.")
        breakdown_time = breakdown_time.sort_values(ascending=False)
        category_percentages = breakdown_time / total_downtime * 100
        filtered_values = category_percentages[category_percentages.cumsum() <= 80]
        vital_few_dict = {i: {subtype: percentage} for i, (subtype, percentage) in enumerate(filtered_values.items(), start=1)}
        if not vital_few_dict:
            major_contributors = category_percentages[(category_percentages.cumsum() > 80) & 
                                                      (category_percentages.cumsum() <= 100)]
            if not major_contributors.empty:
                top_major_contributor = major_contributors.head(1)
                subtype, percentage = top_major_contributor.index[0], top_major_contributor.values[0]
                return {1: {subtype: percentage}}
            return {"message": "There are no major contributors!"}
        return vital_few_dict
    except ValueError as e:
        raise ValueError(f"Value error: {str(e)}")
    except KeyError as e:
        raise KeyError(f"Key error: The expected key '{e}' is missing in the input JSON data.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")



#Function for Decode JWT token
import jwt 
def decodeJwt(token):
    """ Decodes a JWT token to extract user claims.
    Args:
        token (str): The JWT token to decode.
    Returns:
        dict: A dictionary containing user_id, tenantid, and role if available, otherwise None.
    """
    if not token:
        print("Error: No token provided.")
        return None
    try:
        # Attempt to decode the JWT without verifying the signature
        decoded = jwt.decode(token, options={"verify_signature": False})
        # Extract the claims
        claims = decoded.get("https://hasura.io/jwt/claims", {})
        user_id = claims.get("x-hasura-user-id")
        tenantid = claims.get("x-hasura-tenant-id")
        role = claims.get("x-hasura-default-role")
        return {
            "user_id": user_id,
            "V2tenant": tenantid,
            "role": role
        }
    except jwt.ExpiredSignatureError:
        print("Error: The token has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Error: Invalid token.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None



# Colour classification  
def colorClassification(feature_value, max_value, optimization_direction):
    """
    Classifies a feature's value into 'Green', 'Amber', or 'Red' based on thresholds. 
    Args:
        feature_value (float): The value to classify.
        max_value (float): Maximum value for the feature. For percentages, use 100. 
                           For time-based features, use predefined max values:
                           - hour: 3,600,000 ms
                           - day: 86,400,000 ms
                           - week: 604,800,000 ms
                           - month: ~2,592,000,000 ms
                           - year: 31,536,000,000 ms
                           - shift: 83,600,000 ms
        optimization_direction (str): 'maximize' or 'minimize'.
    Returns:
        str: 'Green', 'Amber', or 'Red' based on classification.
    """
    if optimization_direction=='maximize':
        green_threshold = (0.7 * max_value, max_value)
        amber_threshold = (0.3 * max_value, 0.7 * max_value)
        red_threshold = (0, 0.3 * max_value)
    elif optimization_direction=='minimize':
        green_threshold = (0, max_value * 0.3)
        amber_threshold = (max_value * 0.3, max_value * 0.7)
        red_threshold = (max_value * 0.7, max_value)
    if green_threshold[0] <= feature_value <= green_threshold[1]:
        return 'Green'
    elif amber_threshold[0] <= feature_value <= amber_threshold[1]:
        return 'Amber'
    elif red_threshold[0] <= feature_value <= red_threshold[1]:
        return 'Red'
    return 'Red'



# Function for detect Anomalies

def anomaliesDetect(json_data, target_col):
    """
    Identifies outliers in time series data and analyzes their characteristics.
    - Filters out rows with excessive zero values in the target column.
    - Detects extreme high and low values using the IQR method.
    - Summarizes the range and count of outliers, and inspects associated covariate ranges.
    Parameters:
    - json_data: A list of dictionaries containing the data.
    - target_col: The name of the feature (column) to analyze for outliers.
    Returns:
    - A dictionary containing:
    - Count of upper and lower outliers,
    - Ranges of extreme values in the target column,
    - Covariate value ranges corresponding to these outliers.
    Prompt examples:
    - What are the extreme anomalies in the downtime column?
    - List outliers in cycletime and related attribute ranges.
    - Are there high spikes in oee and what features were associated?
    """
    # Step 1: Convert JSON to DataFrame
    df = pd.DataFrame(json_data)
    final_result = []
    for machine in df['machineid'].unique():
        machine_result={}
        machine_data_df = df[df['machineid']==machine]
        # Step 2: Remove rows where target == 0 if they are more than 30%
        zero_target_ratio = (machine_data_df[target_col] == 0).mean()
        if zero_target_ratio > 0.3:
            machine_data_df = machine_data_df[machine_data_df[target_col] != 0]

        # Step 3: Identify columns for IQR outlier removal
        default_cols = ['date','timestamp','hour_of_the_day_x','day_of_the_week','week_of_the_month_x','month_of_the_year','tenantid',
                        'v2tenant','week_of_the_month_y', 'start_timestamp', 'datetime','hour', 'end_timestamp','hour_of_the_day_y']
        null_only_cols = machine_data_df.columns[machine_data_df.isnull().all()].tolist()
        outlier_cols = [
            col for col in machine_data_df.columns
            if col not in default_cols and col not in null_only_cols and col != target_col and machine_data_df[col].dtype in [np.float64, np.int64]
        ]
        
        # Temporarily exclude nulls for IQR outlier removal and mean calculation
        machine_data_df = machine_data_df.loc[machine_data_df[target_col].notna()]  # Filter rows with non-null values
        # Step 4: Remove outliers from data (non-null rows)
        Q1 = machine_data_df[target_col].quantile(0.25)
        Q3 = machine_data_df[target_col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 2 * IQR
        upper = Q3 + 2 * IQR
        # Create outlier flag column for the current column
        outlier_flag_col = f"{target_col}_outlier_flag"
        machine_data_df.loc[:, outlier_flag_col] = None 
        machine_data_df.loc[machine_data_df[target_col] < lower, outlier_flag_col] = 'lower'
        machine_data_df.loc[machine_data_df[target_col] > upper, outlier_flag_col] = 'upper'
        # Store extreme outlier rows
        extreme_values = machine_data_df[(machine_data_df[target_col] < lower) | (machine_data_df[target_col] > upper)]
        # Count how many in each category
        extreme_counts = extreme_values[outlier_flag_col].value_counts().to_dict()
        # Calculate min and max for each category
        extreme_ranges_target = extreme_values.groupby(outlier_flag_col)[target_col].agg(['min', 'max'])
        # calculate min and max for covariates
        cols_to_agg = [col for col in extreme_values.columns if col not in [target_col, outlier_flag_col]]
        # Apply aggregation on those columns
        extreme_ranges_covariates = extreme_values.groupby(outlier_flag_col)[cols_to_agg].agg(['min', 'max'])
        covariate_result = {}
        for _, row in extreme_ranges_covariates.iterrows():
            flag = row['flag'].values[0]
            covariate_result[flag] = {}
            for col in extreme_ranges_covariates.columns.levels[0]:
                if col == 'flag':
                    continue
                min_val = row[(col, 'min')]
                max_val = row[(col, 'max')]
                covariate_result[flag][col] = f"{min_val} - {max_val}"
        # Format output
        machine_result = {
            'machine id': machine,
            'counts of extremes': extreme_counts,
            'range of extremes': f"The extreme low values of the target column {target_col} range from {extreme_ranges_target[(extreme_ranges_target[outlier_flag_col]=='lower')]['min'].values[0]} to {extreme_ranges_target[(extreme_ranges_target[outlier_flag_col]=='lower')]['max'].values[0]} whereas the extreme high values of the target column {target_col} range from {extreme_ranges_target[(extreme_ranges_target[outlier_flag_col]=='upper')]['min'].values[0]} to {extreme_ranges_target[(extreme_ranges_target['outlier_flag_col']=='upper')]['max'].values[0]}",
            'range of corresponding covariates': covariate_result
        }
        final_result.append(machine_result)
    return final_result


# Function for all feactures pareto analysis 

def paretoAnalysis(json_data, category_column, feature_name):
    """
    The getTimePareto function analyzes time loss data provided in JSON format to identify the major contributors based on the Pareto principle.

    Input:
    json_data: A non-empty list of dictionaries where each dictionary contains at least two keys:
    feature_name: The value representing time loss for a specific event.
    category_column: A categorical identifier (e.g., machine ID, downtime type) for grouping the data.
    
    Output:
    A list of dictionaries containing:
    category_column: The name of the category.
    Time_Loss: The total time loss for that category.
    Percent_contribution: The percentage contribution of that category to the total time loss.
    If there are no contributors, a message indicating this is returned.
    """
    try:
        if not isinstance(json_data, list) or not json_data:
            raise ValueError("The input json_data must be a non-empty list.")
        if not isinstance(category_column, str) or not category_column:
            raise ValueError("The category_column must be a non-empty string.")
        df = pd.DataFrame(json_data)
        if df.empty:
            raise ValueError("The DataFrame created from the JSON data is empty.")
        required_columns = [feature_name, category_column]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        df['Time_Loss'] = df[feature_name]
        df = df[df['Time_Loss'] >= 0]
        pareto_df = df.groupby(category_column)['Time_Loss'].sum().reset_index()
        if pareto_df.empty:
            raise ValueError("The grouping operation resulted in an empty DataFrame.")
        pareto_df = pareto_df.sort_values(by='Time_Loss', ascending=False)
        total_loss = pareto_df['Time_Loss'].sum()
        if total_loss == 0:
            raise ValueError("The total Time_Loss is zero, unable to calculate percentages.")
        pareto_df['Percent_contribution'] = pareto_df['Time_Loss'] / total_loss * 100
        pareto_df['Cumulative_Percentage'] = pareto_df['Percent_contribution'].cumsum()
        vital_few_df = pareto_df[pareto_df['Cumulative_Percentage'] <= 80]
        if vital_few_df.empty:
            major_contributors = pareto_df[(pareto_df['Cumulative_Percentage'] > 80) & 
                                            (pareto_df['Cumulative_Percentage'] <= 100)]
            print(major_contributors)
            if not major_contributors.empty:
                return major_contributors.head(1)[[category_column, 'Time_Loss', 'Percent_contribution']].to_dict(orient='records')
            return {"message": "There are no major contributors!"}
        return vital_few_df[[category_column, 'Time_Loss', 'Percent_contribution']].to_dict(orient='records')
    except KeyError as e:
        raise KeyError(f"Key error: The expected key '{e}' is missing in the input JSON data.")
    except ValueError as e:
        raise ValueError(f"Value error: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


# Function to analyze a graph from JSON data
from scipy.signal import argrelextrema
def analyzeGraph(json_data):
    """
    Analyzes a time series graph from JSON data to identify peaks and lows.     
    - Extracts timestamps and values from the JSON data.
    - Identifies peaks and lows using local extrema.
    - Constructs a summary explanation of the trends, including peak and low values.
    Parameters:
    - json_data: A list of dictionaries containing time series data with 'timestamp' and a single parameter.
    Returns:
    - A string summarizing the analysis, including peak and low values, and their timestamps.
    Prompt examples:
    - What are the peaks and lows in the temperature data?  
    - Analyze the pressure trends and identify significant peaks.
    - Summarize the trends in the humidity data.
    """
    # Load JSON data
    data = json_data
    # Identify parameter name dynamically (excluding timestamp)
    parameter_name = [key for key in data[0] if key != "timestamp"][0]
    
    timestamps = [entry["timestamp"] for entry in data]
    values = [entry[parameter_name] for entry in data]
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame({"timestamp": pd.to_datetime(timestamps, unit='ms'), "value": values})
    df = df.groupby("timestamp").sum().reset_index()  # Summing values for duplicate timestamps
    df = df.sort_values("timestamp")
    # Identify peaks and lows
    peak_indices = argrelextrema(df["value"].values, np.greater)[0]
    low_indices = argrelextrema(df["value"].values, np.less)[0]
    peaks = df.iloc[peak_indices]
    lows = df.iloc[low_indices]
    # Construct explanation
    explanation = f"Analyzing parameter: {parameter_name}\n"
    explanation += f"Total data points: {len(df)}\n"
    if not peaks.empty:
        explanation += f"Highest Peak: {peaks['value'].max()} at {peaks.loc[peaks['value'].idxmax(), 'timestamp']}\n"
    else:
        explanation += "No peaks detected.\n"
    if not lows.empty:
        explanation += f"Lowest Point: {lows['value'].min()} at {lows.loc[lows['value'].idxmin(), 'timestamp']}\n"
    else:
        explanation += "No lows detected.\n"
    explanation += "\nDetailed Trends:\n"
    for _, row in peaks.iterrows():
        explanation += f"Peak at {row['timestamp']} with value {row['value']}\n"
    for _, row in lows.iterrows():
        explanation += f"Low at {row['timestamp']} with value {row['value']}\n"
    return explanation

# Function to extract toolpath from G-code blocktext


def extract_toolpath_from_blocktexts(lines):
    """
    Extracts toolpath coordinates from G-code lines.
    Parameters:
    - lines: A list of strings, each representing a line of G-code.
    Returns:
    - A 2D numpy array of points where each point is represented by its X, Y, Z coordinates.
    """
    current_pos = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
    points = []
    for line in lines:
        line = line.strip().upper()
        if line.startswith(('G0', 'G1')):
            for axis in ['X', 'Y', 'Z']:
                match = re.search(f"{axis}(-?\\d+\\.?\\d*)", line)
                if match:
                    current_pos[axis] = float(match.group(1))
            points.append([current_pos['X'], current_pos['Y'], current_pos['Z']])
    return np.array(points)

# Nearest Neighbor Reordering (naive optimizer)
def nearest_neighbor_reorder(points):
    """
    Reorders points using a nearest neighbor algorithm.
    Parameters:
    - points: A 2D numpy array where each row represents a point in 3D space (X, Y, Z).
    Returns:
    - A reordered 2D numpy array of points.
    """
    unvisited = list(points)
    path = [unvisited.pop(0)]
    while unvisited:
        last = path[-1]
        next_index = np.argmin([np.linalg.norm(p - last) for p in unvisited])
        path.append(unvisited.pop(next_index))
    return np.array(path)

# Function to calculate total travel distance between points
def calculate_total_distance(points):
    """
    Calculate the total distance of a path defined by a sequence of points.
    Parameters:
    - points: A 2D numpy array where each row represents a point in 3D space (X, Y, Z).
    Returns:
    - The total distance traveled along the path.
    """
    diffs = np.diff(points, axis=0)
    segment_lengths = np.linalg.norm(diffs, axis=1)
    return np.sum(segment_lengths)
# Function to update G-code with optimized toolpath
def update_gcode_with_optimized_toolpath(original_gcode_lines, optimized_toolpath):
    updated_lines = []
    point_idx = 0
    for line in original_gcode_lines:
        if line.strip().startswith(('G0', 'G1')) and any(c in line for c in 'XYZABCUVW'):
            if point_idx >= len(optimized_toolpath):
                break  # Stop if there are more motion lines than optimized points
            coords = optimized_toolpath[point_idx]
            point_idx += 1
            # Format the new G-code line with X, Y, Z
            new_line = f"G1 X{coords[0]:.3f} Y{coords[1]:.3f} Z{coords[2]:.3f}"
            updated_lines.append(new_line)
        else:
            updated_lines.append(line)
    return updated_lines

# MAIN function: Takes G-code as list of strings (lines)
def optimizedGcode(raw_gcode):
    """
    Optimizes G-code toolpath using nearest neighbor algorithm.
    Parameters:
    - raw_gcode: A string containing G-code commands, each on a new line.
    Returns:
    - A dictionary with updated G-code lines, original distance, optimized distance, and distance reduction.
    """
    # Split raw string into list of lines
    gcode_lines = raw_gcode.strip().split('\n')
    # Extract toolpath from G-code
    toolpaths = extract_toolpath_from_blocktexts(gcode_lines)
    # Optimize toolpath
    optimized_toolpath = nearest_neighbor_reorder(toolpaths)
    # Distance calculations
    original_distance = calculate_total_distance(toolpaths)
    optimized_distance = calculate_total_distance(optimized_toolpath)
    distance_reduction = original_distance - optimized_distance
    # Update G-code lines with optimized path
    updated_gcode = update_gcode_with_optimized_toolpath(gcode_lines, optimized_toolpath)
    return {
        "updated_gcode": updated_gcode,
        "original_distance": f"{original_distance:.2f} mm",
        "optimized_distance": f"{optimized_distance:.2f} mm",
        "distance_reduction": f"{distance_reduction:.2f} mm"
    }

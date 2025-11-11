import json

import numpy as np
import pandas as pd
import tensorflow as tf
import xgboost as xgb
from keras.losses import MeanSquaredError
from sklearn.preprocessing import StandardScaler

from .storage_utils import get_file_from_gridfs

# Define a custom object scope for TensorFlow model loading
custom_objects = {"mse": MeanSquaredError()}

# Define file paths
data_path = get_file_from_gridfs("DNEW2.csv")
soh_model_path = get_file_from_gridfs("soh2_xgboost_model.json")
rul_model_path = get_file_from_gridfs("rul2_lstm_model.h5")


# Load dataset
df = pd.read_csv(data_path)

# Define feature columns
feature_columns = [
    'Year_of_purchase', 'Month_of_purchase', 'Charge_times', 'Charge_duration',
    'Avg_charging_percentage', 'Total_distance_travelled_daily', 'Travel_time_daily',
    'Avg_speed_daily', 'Eco_mode_distance', 'Normal_mode_distance',
    'Sport_mode_distance', 'Hyper_mode_distance'
]

# Load trained models
soh_model = xgb.XGBRegressor()
soh_model.load_model(soh_model_path)
rul_model = tf.keras.models.load_model(rul_model_path, custom_objects=custom_objects)

# Standard scaler
scaler = StandardScaler()
scaler.fit(df[feature_columns])

# Features needing recommendations
features_with_recommendations = [
    "Charge_times", "Charge_duration", "Avg_charging_percentage",
    "Total_distance_travelled_daily", "Travel_time_daily", "Avg_speed_daily",
    "Eco_mode_distance", "Normal_mode_distance", "Sport_mode_distance", "Hyper_mode_distance"
]

# Ideal ranges
ideal_ranges = {
    "Charge_times": (1, 2),
    "Charge_duration": (1, 4),
    "Avg_charging_percentage": (20, 80),
    "Total_distance_travelled_daily": (20, 50),
    "Travel_time_daily": (1, 2),
    "Avg_speed_daily": (20, 50),
    "Eco_mode_distance": (20, 80),
    "Normal_mode_distance": (10, 30),
    "Sport_mode_distance": (0, 10),
    "Hyper_mode_distance": (0, 5)
}

# Range behaviors (dual condition support)
range_behaviors = {
    'Charge_times': ('min_is_not_bad', 'max_is_bad'),
    'Charge_duration': ('min_is_bad', 'max_is_bad'),
    'Avg_charging_percentage': ('min_is_bad', 'max_is_bad'),
    'Total_distance_travelled_daily': ('min_is_good', 'max_is_bad'),
    'Travel_time_daily': ('min_is_not_bad', 'max_is_bad'),
    'Avg_speed_daily': ('min_is_bad', 'max_is_bad'),
    'Eco_mode_distance': ('min_is_bad', 'max_is_good'),
    'Normal_mode_distance': ('min_is_bad', 'max_is_bad'),
    'Sport_mode_distance': ('min_is_not_bad', 'max_is_bad'),
    'Hyper_mode_distance': ('min_is_not_bad', 'max_is_bad')
}

# Recommendations
recommendations = {
    "Charge_times": "Reduce charging frequency to avoid excessive cycles.",
    "Charge_duration": "Do not overcharge beyond the recommended duration.",
    "Avg_charging_percentage": "Maintain charge between 20% and 80% for longer battery life.",
    "Total_distance_travelled_daily": "Excessive daily distance may accelerate battery wear.",
    "Travel_time_daily": "Limit travel time to prevent excessive strain.",
    "Avg_speed_daily": "Keep speed within the optimal range for efficiency.",
    "Eco_mode_distance": "Try using more Eco mode to maximize range.",
    "Normal_mode_distance": "Balance Normal mode usage to avoid inefficiency.",
    "Sport_mode_distance": "Limit Sport mode usage to conserve energy.",
    "Hyper_mode_distance": "Hyper mode should be used sparingly to prevent rapid degradation."
}

# Set this to False for Revolt (raw km values), True for OLA (percentages)
values_are_percent = True

def evaluate_input(user_input):
    issues = []
    try:
        # ✅ Convert all values to float first
        user_input = {k: float(v) for k, v in user_input.items()}
        total_distance = user_input["Total_distance_travelled_daily"]

        for feature in features_with_recommendations:
            value = user_input[feature]
            min_val, max_val = ideal_ranges[feature]

            if feature in ["Eco_mode_distance", "Normal_mode_distance", 
                           "Sport_mode_distance", "Hyper_mode_distance"]:
                if total_distance == 0:
                    continue
                percent = (value / total_distance) * 100
                if not (min_val <= percent <= max_val):
                    issues.append(f"{feature}: {recommendations[feature]}")
            else:
                if not (min_val <= value <= max_val):
                    issues.append(f"{feature}: {recommendations[feature]}")
    except Exception as e:
        print("🔥 Error in ola_recommendations:", e)
        issues.append(f"Invalid input: {str(e)}")

    return issues if issues else ["GOOD"]




def predict_soh_rul(user_input):
    try:
        # Convert all string values to float
        for key in user_input:
            user_input[key] = float(user_input[key])  # ✅ force numeric

        input_features = [user_input[feature] for feature in feature_columns]
        input_df = pd.DataFrame([input_features], columns=feature_columns)
        user_input_scaled = scaler.transform(input_df)

        predicted_soh = soh_model.predict(user_input_scaled)[0]
        user_input_lstm = user_input_scaled.reshape((1, 1, len(feature_columns)))
        predicted_rul = rul_model.predict(user_input_lstm)[0][0]

        return predicted_soh, predicted_rul
    except Exception as e:
        print("🔥 Prediction error:", e)
        raise

# import json
# import numpy as np
# import xgboost as xgb
# import tensorflow as tf
# import pandas as pd
# from sklearn.preprocessing import StandardScaler
# from keras.losses import MeanSquaredError

# # Paths (change as per deployment)
# data_path = r"C:\Users\Aditi\Desktop\evpaths\DNEW2.csv"
# soh_model_path = r"C:\Users\Aditi\Desktop\evpaths\soh_xgboost_model.json"
# rul_model_path = r"C:\Users\Aditi\Desktop\evpaths\rul_lstm_model.h5"

# # Load dataset
# df = pd.read_csv(data_path)

# # Feature columns
# feature_columns = [
#     'Year_of_purchase', 'Month_of_purchase', 'Charge_times', 'Charge_duration',
#     'Avg_charging_percentage', 'Total_distance_travelled_daily', 'Travel_time_daily',
#     'Avg_speed_daily', 'Eco_mode_distance', 'Normal_mode_distance',
#     'Sport_mode_distance', 'Hyper_mode_distance'
# ]

# # Load and fit scaler
# scaler = StandardScaler()
# scaler.fit(df[feature_columns])

# # Load models
# soh_model = xgb.XGBRegressor()
# soh_model.load_model(soh_model_path)

# rul_model = tf.keras.models.load_model(
#     rul_model_path, custom_objects={"mse": MeanSquaredError()}
# )

# # Ideal ranges for evaluation
# ideal_ranges = {
#     "Charge_times": (1, 2),
#     "Charge_duration": (1, 4),
#     "Avg_charging_percentage": (20, 80),
#     "Total_distance_travelled_daily": (20, 50),
#     "Travel_time_daily": (1, 2),
#     "Avg_speed_daily": (20, 40),
#     "Eco_mode_distance": (60, 80),
#     "Normal_mode_distance": (20, 30),
#     "Sport_mode_distance": (5, 10),
#     "Hyper_mode_distance": (1, 5)
# }

# recommendations = {
#     "Charge_times": "Reduce charging frequency to avoid excessive cycles.",
#     "Charge_duration": "Do not overcharge beyond the recommended duration.",
#     "Avg_charging_percentage": "Maintain charge between 20% and 80% for longer battery life.",
#     "Total_distance_travelled_daily": "Excessive daily distance may accelerate battery wear.",
#     "Travel_time_daily": "Limit travel time to prevent excessive strain.",
#     "Avg_speed_daily": "Keep speed within the optimal range for efficiency.",
#     "Eco_mode_distance": "Try using more Eco mode to maximize range.",
#     "Normal_mode_distance": "Balance Normal mode usage to avoid inefficiency.",
#     "Sport_mode_distance": "Limit Sport mode usage to conserve energy.",
#     "Hyper_mode_distance": "Hyper mode should be used sparingly to prevent rapid degradation."
# }

# def evaluate_input(user_input):
#     """Return list of recommendations or GOOD if all inputs are in range."""
#     issues = []
#     for key, (min_val, max_val) in ideal_ranges.items():
#         val = user_input.get(key)
#         if val is not None and not (min_val <= val <= max_val):
#             issues.append(recommendations[key])
#     return issues if issues else ["GOOD"]

# def predict_soh_rul(user_input):
#     """Return predicted SOH and RUL."""
#     input_data = [user_input.get(f) for f in feature_columns]
#     input_scaled = scaler.transform([input_data])

#     soh = soh_model.predict(input_scaled)[0]
#     lstm_input = input_scaled.reshape((1, 1, len(feature_columns)))
#     rul = rul_model.predict(lstm_input)[0][0]

#     return soh, rul

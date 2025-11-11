import json
import numpy as np
import pandas as pd
import tensorflow as tf
import xgboost as xgb
from keras.losses import MeanSquaredError
from sklearn.preprocessing import StandardScaler

# Define custom objects for loading the LSTM model
custom_objects = {"mse": MeanSquaredError()}

# File paths
DATA_PATH = r"C:\Users\Aditi\Desktop\revoltevpaths\RV4.csv"
SOH_MODEL_PATH = r"C:\Users\Aditi\Desktop\revoltevpaths\soh1_model.json"
RUL_MODEL_PATH = r"C:\Users\Aditi\Desktop\revoltevpaths\rul1_model.h5"

# Load dataset
df = pd.read_csv(DATA_PATH)

df.rename(columns={
    'Distance_Travelled(km)': 'Distance_Travelled',
    'Ride_Time(mins)': 'RideTime',
    'Average_Speed(km/hr)': 'Average_Speed',
    'Max_Speed(km/hr)': 'Max_Speed',
    'Eco_Mode(%)': 'Eco_Mode',
    'Normal_Mode(%)': 'Normal_Mode',
    'Sport_Mode(%)': 'Sport_Mode',
    'SOC_Consumed(%)': 'SOC_Consumed'
}, inplace=True)

feature_columns = [
    'Distance_Travelled', 'RideTime', 'Average_Speed', 'Max_Speed',
    'Eco_Mode', 'Normal_Mode', 'Sport_Mode', 'SOC_Consumed', 'Year_of_purchase', 'Month_of_purchase'
]

# Load models
soh_model = xgb.XGBRegressor()
soh_model.load_model(SOH_MODEL_PATH)
rul_model = tf.keras.models.load_model(RUL_MODEL_PATH, custom_objects=custom_objects)

# StandardScaler setup
scaler = StandardScaler()
scaler.fit(df[feature_columns])

# Ideal feature ranges for recommendations
ideal_ranges = {
    'Distance_Travelled': (30, 80),
    'RideTime': (60, 100),
    'Average_Speed': (20, 45),
    'Max_Speed': (60, 70),
    'Eco_Mode': (60, 80),
    'Normal_Mode': (20, 45),
    'Sport_Mode': (0, 10),
    'SOC_Consumed': (10, 60)
}

# Define detailed range behaviors
range_behaviors = {
    'Distance_Travelled': ('min_is_good', 'max_is_bad'),
    'RideTime': ('min_is_not_bad', 'max_is_bad'),
    'Average_Speed': ('min_is_bad', 'max_is_bad'),
    'Max_Speed': ('min_is_not_bad', 'max_is_bad'),
    'Eco_Mode': ('min_is_bad', 'max_is_good'),
    'Normal_Mode': ('min_is_bad', 'max_is_bad'),
    'Sport_Mode': ('min_is_not_bad', 'max_is_bad'),
    'SOC_Consumed': ('min_is_not_bad', 'max_is_bad')
}

recommendations = {
    'Distance_Travelled': "Keep distance traveled moderate to optimize battery performance.",
    'RideTime': "Avoid excessively long rides to reduce battery degradation.",
    'Average_Speed': "Maintain a steady average speed for better efficiency.",
    'Max_Speed': "Limit maximum speed for prolonged battery life.",
    'Eco_Mode': "Increase Eco Mode usage to extend range.",
    'Normal_Mode': "Balance Normal Mode usage appropriately.",
    'Sport_Mode': "Minimize Sport Mode to prevent high discharge rates.",
    'SOC_Consumed': "Avoid deep discharges; keep SOC within healthy range."
}

def evaluate_input(data):
    issues = []
    for key in ideal_ranges:
        try:
            value = float(data[key])
            min_val, max_val = ideal_ranges[key]
            behavior = range_behaviors.get(key, ("both_bad", "both_bad"))
            min_behavior, max_behavior = behavior

            if min_behavior == "min_is_bad" and value < min_val:
                issues.append(f"{key}: {recommendations[key]}")
            elif min_behavior == "min_is_good" and value >= min_val:
                continue
            elif min_behavior == "min_is_good" and value < min_val:
                continue

            if max_behavior == "max_is_bad" and value > max_val:
                issues.append(f"{key}: {recommendations[key]}")
            elif max_behavior == "max_is_good" and value <= max_val:
                continue
            elif max_behavior == "max_is_good" and value > max_val:
                continue

        except Exception as e:
            issues.append(f"{key}: Invalid input - {str(e)}")
    return issues if issues else ["GOOD"]

def predict_soh_rul(data):
    try:
        input_values = [float(data[key]) for key in feature_columns]
        input_df = pd.DataFrame([input_values], columns=feature_columns)
        scaled_input = scaler.transform(input_df)

        # Predict SOH using XGBoost
        soh = soh_model.predict(scaled_input)[0]

        # Predict RUL using LSTM
        reshaped_input = scaled_input.reshape((1, 1, len(feature_columns)))
        rul = rul_model.predict(reshaped_input)[0][0]

        return round(float(soh), 2), round(float(rul), 2)
    except Exception as e:
        print("🔥 Prediction error:", e)
        raise
    

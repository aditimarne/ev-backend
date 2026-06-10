import pandas as pd
import tensorflow as tf
import xgboost as xgb
from keras.losses import MeanSquaredError
from sklearn.preprocessing import StandardScaler

from .storage_utils import get_file_from_gridfs

# TensorFlow custom objects
custom_objects = {"mse": MeanSquaredError()}

# GLOBAL LAZY OBJECTS

_df = None
_scaler = None
_soh_model = None
_rul_model = None


feature_columns = [
    'Year_of_purchase', 'Month_of_purchase', 'Charge_times', 'Charge_duration',
    'Avg_charging_percentage', 'Total_distance_travelled_daily',
    'Travel_time_daily', 'Avg_speed_daily', 'Eco_mode_distance',
    'Normal_mode_distance', 'Sport_mode_distance', 'Hyper_mode_distance'
]

features_with_recommendations = [
    "Charge_times", "Charge_duration", "Avg_charging_percentage",
    "Total_distance_travelled_daily", "Travel_time_daily", "Avg_speed_daily",
    "Eco_mode_distance", "Normal_mode_distance",
    "Sport_mode_distance", "Hyper_mode_distance"
]


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

recommendations = {
    "Charge_times": "Reduce charging frequency to avoid excessive cycles.",
    "Charge_duration": "Do not overcharge beyond the recommended duration.",
    "Avg_charging_percentage": "Maintain charge between 20% and 80%.",
    "Total_distance_travelled_daily": "Excessive distance accelerates wear.",
    "Travel_time_daily": "Limit travel time to reduce strain.",
    "Avg_speed_daily": "Maintain optimal speed.",
    "Eco_mode_distance": "Use Eco mode more.",
    "Normal_mode_distance": "Balance Normal mode usage.",
    "Sport_mode_distance": "Limit Sport mode.",
    "Hyper_mode_distance": "Use Hyper mode sparingly."
}

# LAZY LOADER

def load_resources():
    global _df, _scaler, _soh_model, _rul_model

    if _df is None:
        data_path = get_file_from_gridfs("DNEW2.csv")
        _df = pd.read_csv(data_path)

        _scaler = StandardScaler()
        _scaler.fit(_df[feature_columns])

    if _soh_model is None:
        soh_path = get_file_from_gridfs("soh2_xgboost_model.json")
        _soh_model = xgb.XGBRegressor()
        _soh_model.load_model(soh_path)

    tf.keras.backend.clear_session()

    if _rul_model is None:
        rul_path = get_file_from_gridfs("rul2_lstm_model_v2.h5")
        tf.keras.backend.clear_session()
        _rul_model = tf.keras.models.load_model(
            rul_path,
            compile=False,
            custom_objects={
            **custom_objects,
                'InputLayer': tf.keras.layers.InputLayer
            }
        )   


def evaluate_input(user_input):
    issues = []
    user_input = {k: float(v) for k, v in user_input.items()}
    total_distance = user_input["Total_distance_travelled_daily"]

    for feature in features_with_recommendations:
        value = user_input[feature]
        min_val, max_val = ideal_ranges[feature]

        if feature in [
            "Eco_mode_distance", "Normal_mode_distance",
            "Sport_mode_distance", "Hyper_mode_distance"
        ]:
            if total_distance == 0:
                continue
            percent = (value / total_distance) * 100
            if not (min_val <= percent <= max_val):
                issues.append(f"{feature}: {recommendations[feature]}")
        else:
            if not (min_val <= value <= max_val):
                issues.append(f"{feature}: {recommendations[feature]}")

    return issues if issues else ["GOOD"]


def predict_soh_rul(user_input):
    load_resources()

    user_input = {k: float(v) for k, v in user_input.items()}
    input_df = pd.DataFrame(
        [[user_input[col] for col in feature_columns]],
        columns=feature_columns
    )

    scaled = _scaler.transform(input_df)

    soh = _soh_model.predict(scaled)[0]
    rul = _rul_model.predict(
        scaled.reshape((1, 1, len(feature_columns)))
    )[0][0]

    return soh, rul

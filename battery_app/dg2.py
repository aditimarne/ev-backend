import pandas as pd
import tensorflow as tf
import xgboost as xgb
from keras.losses import MeanSquaredError
from sklearn.preprocessing import StandardScaler

from .storage_utils import get_file_from_gridfs

custom_objects = {"mse": MeanSquaredError()}

_df = None
_scaler = None
_soh_model = None
_rul_model = None


feature_columns = [
    'Distance_Travelled', 'RideTime', 'Average_Speed', 'Max_Speed',
    'Eco_Mode', 'Normal_Mode', 'Sport_Mode', 'SOC_Consumed',
    'Year_of_purchase', 'Month_of_purchase'
]

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

recommendations = {
    'Distance_Travelled': "Keep distance traveled moderate.",
    'RideTime': "Avoid long rides.",
    'Average_Speed': "Maintain steady speed.",
    'Max_Speed': "Limit top speed.",
    'Eco_Mode': "Increase Eco mode usage.",
    'Normal_Mode': "Balance Normal mode.",
    'Sport_Mode': "Limit Sport mode.",
    'SOC_Consumed': "Avoid deep discharge."
}


def load_resources():
    global _df, _scaler, _soh_model, _rul_model

    if _df is None:
        data_path = get_file_from_gridfs("RV4.csv")
        _df = pd.read_csv(data_path)

        _df.rename(columns={
            'Distance_Travelled(km)': 'Distance_Travelled',
            'Ride_Time(mins)': 'RideTime',
            'Average_Speed(km/hr)': 'Average_Speed',
            'Max_Speed(km/hr)': 'Max_Speed',
            'Eco_Mode(%)': 'Eco_Mode',
            'Normal_Mode(%)': 'Normal_Mode',
            'Sport_Mode(%)': 'Sport_Mode',
            'SOC_Consumed(%)': 'SOC_Consumed'
        }, inplace=True)

        _scaler = StandardScaler()
        _scaler.fit(_df[feature_columns])

    if _soh_model is None:
        soh_path = get_file_from_gridfs("soh1_model.json")
        _soh_model = xgb.XGBRegressor()
        _soh_model.load_model(soh_path)


    if _rul_model is None:
        rul_path = get_file_from_gridfs("rul1_model_v2.h5")
        tf.keras.backend.clear_session()
        _rul_model = tf.keras.models.load_model(
            rul_path,
            compile=False,
            custom_objects={
                **custom_objects,
                    'InputLayer': tf.keras.layers.InputLayer
            }
        )


def evaluate_input(data):
    issues = []
    data = {k: float(v) for k, v in data.items()}

    for key, (min_v, max_v) in ideal_ranges.items():
        if not (min_v <= data[key] <= max_v):
            issues.append(f"{key}: {recommendations[key]}")

    return issues if issues else ["GOOD"]


def predict_soh_rul(data):
    load_resources()

    data = {k: float(v) for k, v in data.items()}
    input_df = pd.DataFrame(
        [[data[col] for col in feature_columns]],
        columns=feature_columns
    )

    scaled = _scaler.transform(input_df)

    soh = _soh_model.predict(scaled)[0]
    rul = _rul_model.predict(
        scaled.reshape((1, 1, len(feature_columns)))
    )[0][0]

    return round(float(soh), 2), round(float(rul), 2)

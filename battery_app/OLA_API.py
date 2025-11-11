# # OLA_API.py
# OLA_API.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . import dg1  # Import your digital twin logic

@csrf_exempt
def ola_predict(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("🔍 Incoming data:", data)  # Add this line

            predicted_soh, predicted_rul = dg1.predict_soh_rul(data)
            advice = dg1.evaluate_input(data)

            return JsonResponse({
                'soh': round(float(predicted_soh), 2),
                'rul': round(float(predicted_rul), 2),
                'recommendations': advice
            })

        except Exception as e:
            print("🔥 Prediction error:", e)  # Add this line
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

@csrf_exempt
def ola_recommendations(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recommendations = dg1.evaluate_input(data)
            return JsonResponse({
                'title': "Ola Battery Suggestions",
                'suggestions': recommendations
            })
        except Exception as e:
            print("🔥 Error in ola_recommendations:", e)
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)














# import json
# import numpy as np
# import xgboost as xgb
# import tensorflow as tf
# from sklearn.preprocessing import StandardScaler
# import pandas as pd
# from keras.losses import MeanSquaredError
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# # Define a custom object scope for TensorFlow model loading
# custom_objects = {"mse": MeanSquaredError()}

# # Define file paths
# data_path = r"C:\Users\Aditi\Desktop\evpaths\DNEW2.csv"
# soh_model_path = r"C:\Users\Aditi\Desktop\evpaths\soh_xgboost_model.json"
# rul_model_path = r"C:\Users\Aditi\Desktop\evpaths\rul_lstm_model.h5"

# # Load dataset and scaler
# df = pd.read_csv(data_path)
# feature_columns = ['Year_of_purchase', 'Month_of_purchase', 'Charge_times', 'Charge_duration', 'Avg_charging_percentage', 
#                    'Total_distance_travelled_daily', 'Travel_time_daily', 'Avg_speed_daily', 'Eco_mode_distance',
#                    'Normal_mode_distance', 'Sport_mode_distance', 'Hyper_mode_distance']

# scaler = StandardScaler()
# scaler.fit(df[feature_columns])

# # Load models
# soh_model = xgb.XGBRegressor()
# soh_model.load_model(soh_model_path)
# rul_model = tf.keras.models.load_model(rul_model_path, custom_objects=custom_objects)

# # Ideal feature ranges for recommendations
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
#     issues = []
#     for feature in ideal_ranges:
#         value = user_input.get(feature, None)
#         if value is not None:
#             min_val, max_val = ideal_ranges[feature]
#             if not (min_val <= value <= max_val):
#                 issues.append(recommendations[feature])
#     return issues if issues else ["GOOD"]

# @csrf_exempt
# def ola_predict(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             input_features = [data.get(feature) for feature in feature_columns]
#             scaled_input = scaler.transform([input_features])

#             # SOH Prediction
#             predicted_soh = soh_model.predict(scaled_input)[0]

#             # RUL Prediction
#             lstm_input = scaled_input.reshape((1, 1, len(feature_columns)))
#             predicted_rul = rul_model.predict(lstm_input)[0][0]

#             advice = evaluate_input(data)

#             return JsonResponse({
#                 'soh': float(predicted_soh),
#                 'rul': float(predicted_rul),
#                 'recommendations': advice
#             })
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Only POST method allowed'}, status=405)

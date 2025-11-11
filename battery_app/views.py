# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# from .utils import predict_soh_rul, evaluate_input

# @csrf_exempt
# def ola_predict(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             required_fields = [
#                 'Year_of_purchase', 'Month_of_purchase', 'Charge_times', 'Charge_duration',
#                 'Avg_charging_percentage', 'Total_distance_travelled_daily', 'Travel_time_daily',
#                 'Avg_speed_daily', 'Eco_mode_distance', 'Normal_mode_distance',
#                 'Sport_mode_distance', 'Hyper_mode_distance'
#             ]

#             missing = [f for f in required_fields if f not in data]
#             if missing:
#                 return JsonResponse({"error": f"Missing fields: {missing}"}, status=400)

#             soh, rul = predict_soh_rul(data)
#             advice = evaluate_input(data)

#             return JsonResponse({
#                 "SOH": round(soh, 2),
#                 "RUL (months)": round(rul, 2),
#                 "Recommendations": advice
#             })

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     return JsonResponse({"error": "Only POST method is allowed"}, status=405)

from fastapi import APIRouter, HTTPException
from battery_app import dg1

router = APIRouter()

@router.post("/predict")
def ola_predict(data: dict):
    try:
        soh, rul = dg1.predict_soh_rul(data)
        advice = dg1.evaluate_input(data)
        return {
            "soh": round(float(soh), 2),
            "rul": round(float(rul), 2),
            "recommendations": advice
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations")
def ola_recommend(data: dict):
    try:
        advice = dg1.evaluate_input(data)
        return {"suggestions": advice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))












# # OLA_API.py
# OLA_API.py

# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from . import dg1  # Import your digital twin logic

# @csrf_exempt
# def ola_predict(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             print("🔍 Incoming data:", data)  # Add this line

#             predicted_soh, predicted_rul = dg1.predict_soh_rul(data)
#             advice = dg1.evaluate_input(data)

#             return JsonResponse({
#                 'soh': round(float(predicted_soh), 2),
#                 'rul': round(float(predicted_rul), 2),
#                 'recommendations': advice
#             })

#         except Exception as e:
#             print("🔥 Prediction error:", e)  # Add this line
#             return JsonResponse({'error': str(e)}, status=500)

#     else:
#         return JsonResponse({'error': 'Only POST method allowed'}, status=405)

# @csrf_exempt
# def ola_recommendations(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             recommendations = dg1.evaluate_input(data)
#             return JsonResponse({
#                 'title': "Ola Battery Suggestions",
#                 'suggestions': recommendations
#             })
#         except Exception as e:
#             print("🔥 Error in ola_recommendations:", e)
#             return JsonResponse({'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Only POST method allowed'}, status=405)














